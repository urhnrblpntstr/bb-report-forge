"""
bb-report-forge — intake auto-evaluator.

Scans ./bb-inputs/ and classifies files into the three categories
the skill needs: scope, guidelines, template. Writes the result to
bb-inputs/manifest.json and prints a human-readable summary.

This script is pure-stdlib Python. No third-party deps. It runs
*outside* the adversarial review loop — it is the intake helper,
not a reviewer.

USAGE
    python scan_inputs.py            # uses ./bb-inputs relative to CWD
    python scan_inputs.py /path/to/bb-inputs

EXIT CODES
    0  — all three categories resolved (possibly with empty placeholders
         for the ones the user has to fill in)
    2  — at least one category has ambiguous matches and needs the user
         to disambiguate; the manifest records the candidates
    3  — at least one category has zero candidates

The skill handles exit codes 2 and 3 by asking the user, not by guessing.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


# --------------------------------------------------------------------------- #
# Filename hints                                                              #
# --------------------------------------------------------------------------- #
# Lowercased basename → category. A file matches a hint if its basename
# (without extension) contains the hint as a word/segment. "scope" matches
# "scope.md", "my-scope.md", "scope_doc.txt". It does NOT match "telescope.md".
#
# These are *hints*, not rules. The content classifier (§2) is the source of
# truth when it disagrees with the hint.

FILENAME_HINTS: dict[str, list[str]] = {
    "scope": [
        "scope",
        "targets",
        "wildcards",
        "in-scope",
        "inscope",
        "assets",
        "domains",
    ],
    "guidelines": [
        "guideline",
        "guidelines",
        "policy",
        "policies",
        "rules",
        "testing-rules",
        "rules-of-engagement",
        "roe",
        "disclosure",
        "bounty",
    ],
    "template": [
        "template",
        "tempalate",  # common typo — kept deliberately
        "templete",   # another common typo — kept deliberately
        "report-template",
        "submission",
    ],
}

# Extensions associated with each category. Used as a tiebreaker when the
# filename hint is missing and the content classifier is also uncertain.
EXTENSION_HINTS: dict[str, set[str]] = {
    "scope": {".csv", ".tsv", ".txt", ".json", ".yaml", ".yml"},
    "guidelines": {".md", ".txt", ".pdf"},  # PDF is hint-only; content is opaque
    "template": {".md", ".txt", ".html"},
}


# --------------------------------------------------------------------------- #
# Content fingerprints                                                        #
# --------------------------------------------------------------------------- #
# Regex patterns that, if found in a file's first ~16KB, indicate a category.
# Confidence scoring: each match adds to a per-category score. Highest score
# wins. Ties go to the user as ambiguous.
#
# These patterns are deliberately conservative — false negatives (asking the
# user to confirm) are cheaper than false positives (silently misclassifying
# a guideline as a scope file).

SCOPE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bin[\s-]?scope\b", re.IGNORECASE),
    re.compile(r"\bout[\s-]?of[\s-]?scope\b", re.IGNORECASE),
    re.compile(r"\bexcluded?\b", re.IGNORECASE),
    re.compile(r"\bwildcard[s]?\b", re.IGNORECASE),
    re.compile(r"\basset[s]?\b", re.IGNORECASE),
    re.compile(r"\bdomain[s]?\b.*\.(com|net|org|io|ai|app|dev)\b", re.IGNORECASE),
    re.compile(r"\*\.[a-z0-9-]+\.[a-z]{2,}", re.IGNORECASE),  # *.example.com
    re.compile(r"\bscope\s*[:=]", re.IGNORECASE),
]

GUIDELINES_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bguideline[s]?\b", re.IGNORECASE),
    re.compile(r"\brule[s]? of (engagement|conduct)\b", re.IGNORECASE),
    re.compile(r"\btesting rules\b", re.IGNORECASE),
    re.compile(r"\bresponsible disclosure\b", re.IGNORECASE),
    re.compile(r"\bdo[sn']?t\s+(test|scan|use)\b", re.IGNORECASE),
    re.compile(r"\bprohibit", re.IGNORECASE),
    re.compile(r"\bseverity\s*[:=]\s*(critical|high|medium|low)", re.IGNORECASE),
    re.compile(r"\bbounty\b", re.IGNORECASE),
    re.compile(r"\breward\b", re.IGNORECASE),
    re.compile(r"\b90[\s-]?day", re.IGNORECASE),
]

TEMPLATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^#\s*title\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^##\s*(severity|cvss|asset|summary|reproduction|impact|remediation)\s*$",
               re.IGNORECASE | re.MULTILINE),
    re.compile(r"\bcvss\s*(v?3|v?4)?\.?\d?(\.\d)?\b", re.IGNORECASE),
    re.compile(r"^>\s*severity defaults?\s*:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"<!--[\s\S]*?-->", re.IGNORECASE),  # HTML comment in template
]


# --------------------------------------------------------------------------- #
# Data model                                                                  #
# --------------------------------------------------------------------------- #

@dataclass
class FileCandidate:
    path: str                       # absolute or input-dir-relative
    relpath: str                    # path relative to bb-inputs/
    basename: str
    extension: str
    size_bytes: int
    content_sha256: str
    extension_hint: str | None      # category suggested by extension, or None
    filename_hint: str | None       # category suggested by basename, or None
    content_scores: dict[str, int]  # category → score
    final_category: str | None      # best-guess category, or None
    confidence: float               # 0.0–1.0 spread between top-1 and top-2
    ambiguous_with: list[str] = field(default_factory=list)
    # ^ other categories whose score is within `AMBIGUITY_TOLERANCE` of the top


@dataclass
class Manifest:
    generated_at: str
    input_dir: str
    files: list[FileCandidate]
    resolved: dict[str, str | None]   # category → path, or None
    ambiguous: dict[str, list[str]]   # category → list of candidate paths
    missing: list[str]                # categories with zero candidates
    notes: list[str]


AMBIGUITY_TOLERANCE = 2  # if top-2 scores differ by ≤ this, ask the user
SNIFF_BYTES = 16 * 1024  # how much of each file to read for fingerprinting


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _basename_without_ext(path: Path) -> str:
    return path.stem.lower()


def _filename_hint(basename: str) -> str | None:
    """Return the category whose hint list contains a word in `basename`.

    A "word" here is a hyphen- or underscore-separated segment. This avoids
    matching "telescope" → "scope".
    """
    # Split on common separators
    segments = re.split(r"[-_\s]+", basename)
    # Also check the full basename for compound hints like "in-scope"
    segments.append(basename)
    for category, hints in FILENAME_HINTS.items():
        for hint in hints:
            for seg in segments:
                if seg == hint or hint in seg.split("-"):
                    return category
    return None


def _extension_hint(extension: str) -> str | None:
    extension = extension.lower()
    for category, exts in EXTENSION_HINTS.items():
        if extension in exts:
            return category
    return None


def _score_content(text: str, patterns: list[re.Pattern[str]]) -> int:
    return sum(1 for p in patterns if p.search(text))


def _sha256_of_file(path: Path, sniff_bytes: int = SNIFF_BYTES) -> str:
    """Hash the first `sniff_bytes` of a file. Same input → same hash, so
    duplicate files (e.g. a copy of scope.md in a subfolder) collapse to one
    candidate in the manifest after dedup."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(sniff_bytes))
    return h.hexdigest()[:16]  # short hash is enough for de-dup display


def _read_text_sniff(path: Path, sniff_bytes: int = SNIFF_BYTES) -> str:
    """Read up to `sniff_bytes` of a file as text. Binary files (PDF, ZIP)
    return an empty string — the content classifier cannot fingerprint them,
    and the skill will surface that to the user."""
    try:
        with open(path, "rb") as f:
            raw = f.read(sniff_bytes)
        # Strip nulls; treat as latin-1 to never crash on weird encodings
        return raw.replace(b"\x00", b"").decode("latin-1", errors="replace")
    except OSError:
        return ""


# --------------------------------------------------------------------------- #
# Core scan                                                                   #
# --------------------------------------------------------------------------- #

def scan(input_dir: Path) -> Manifest:
    if not input_dir.is_dir():
        # Graceful first-run: create the inputs dir rather than crashing, and
        # return a manifest that reports all three categories missing. The skill
        # then asks the user to drop scope + guidelines (+ optional template).
        input_dir.mkdir(parents=True, exist_ok=True)
        return Manifest(
            generated_at=datetime.now(timezone.utc).isoformat(),
            input_dir=str(input_dir.resolve()),
            files=[],
            resolved={"scope": None, "guidelines": None, "template": None},
            ambiguous={"scope": [], "guidelines": [], "template": []},
            missing=["scope", "guidelines", "template"],
            notes=[f"Created empty {input_dir} — drop scope, guidelines, and "
                   "(optionally) a report template here, then re-run."],
        )

    candidates: list[FileCandidate] = []

    for path in sorted(input_dir.iterdir()):
        if not path.is_file():
            continue
        # Skip dotfiles and the manifest itself
        if path.name.startswith("."):
            continue
        if path.name == "manifest.json":
            continue

        relpath = str(path.relative_to(input_dir))
        basename = _basename_without_ext(path)
        extension = path.suffix

        text = _read_text_sniff(path)
        scores = {
            "scope": _score_content(text, SCOPE_PATTERNS),
            "guidelines": _score_content(text, GUIDELINES_PATTERNS),
            "template": _score_content(text, TEMPLATE_PATTERNS),
        }

        candidates.append(FileCandidate(
            path=str(path.resolve()),
            relpath=relpath,
            basename=path.name,
            extension=extension,
            size_bytes=path.stat().st_size,
            content_sha256=_sha256_of_file(path),
            extension_hint=_extension_hint(extension),
            filename_hint=_filename_hint(basename),
            content_scores=scores,
            final_category=None,
            confidence=0.0,
        ))

    # For each candidate, decide its final_category
    for c in candidates:
        # Combined "support" per category = max(filname, extension) + content score
        support: dict[str, int] = {}
        for cat in ("scope", "guidelines", "template"):
            base = 0
            if c.filename_hint == cat:
                base += 5
            if c.extension_hint == cat:
                base += 3
            support[cat] = base + c.content_scores[cat]

        ranked = sorted(support.items(), key=lambda kv: (-kv[1], kv[0]))
        top_cat, top_score = ranked[0]
        second_cat, second_score = ranked[1] if len(ranked) > 1 else (None, -1)

        if top_score <= 0:
            c.final_category = None
            c.confidence = 0.0
            continue

        c.final_category = top_cat
        # Confidence is 0.0–1.0 based on the gap between top-1 and top-2
        gap = top_score - max(second_score, 0)
        c.confidence = min(1.0, gap / 5.0)

        if second_score > 0 and (top_score - second_score) <= AMBIGUITY_TOLERANCE:
            c.ambiguous_with.append(second_cat)

    # Resolve per-category: pick the highest-confidence candidate, but
    # if 2+ candidates map to the same category and their confidences are
    # within tolerance, mark the category as ambiguous.
    resolved: dict[str, str | None] = {"scope": None, "guidelines": None, "template": None}
    ambiguous: dict[str, list[str]] = {"scope": [], "guidelines": [], "template": []}

    for cat in ("scope", "guidelines", "template"):
        matches = [c for c in candidates if c.final_category == cat]
        if not matches:
            continue
        # If any match is itself flagged ambiguous_with another category,
        # the file is genuinely uncertain — surface the whole category.
        if any(m.ambiguous_with for m in matches):
            ambiguous[cat] = [m.relpath for m in matches]
            continue
        # Otherwise pick the highest-confidence match
        matches.sort(key=lambda c: (-c.confidence, c.basename))
        top, second = matches[0], (matches[1] if len(matches) > 1 else None)
        if second and (top.confidence - second.confidence) <= 0.2:
            ambiguous[cat] = [m.relpath for m in matches]
        else:
            resolved[cat] = matches[0].relpath

    missing = [cat for cat, path in resolved.items() if path is None and not ambiguous[cat]]

    notes: list[str] = []
    # If a category is missing and a generic file (no hint, no content match)
    # is sitting in the dir, surface it as a fallback candidate.
    generic = [c for c in candidates if c.final_category is None]
    if generic:
        notes.append(
            "Generic file(s) with no clear category match: "
            + ", ".join(c.relpath for c in generic)
            + ". The skill will ask you to confirm which category each belongs to."
        )

    return Manifest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        input_dir=str(input_dir.resolve()),
        files=candidates,
        resolved=resolved,
        ambiguous=ambiguous,
        missing=missing,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #

def _print_summary(m: Manifest) -> None:
    print(f"bb-inputs auto-evaluator — scanned {m.input_dir}")
    print(f"  generated: {m.generated_at}")
    print(f"  files:     {len(m.files)}")
    print()
    print("  resolved:")
    for cat, path in m.resolved.items():
        if path:
            print(f"    {cat:11s}  ->  {path}")
    print()
    print("  ambiguous (will ask you to disambiguate):")
    any_amb = False
    for cat, paths in m.ambiguous.items():
        if paths:
            any_amb = True
            print(f"    {cat:11s}  ->  {', '.join(paths)}")
    if not any_amb:
        print("    (none)")
    print()
    print("  missing:")
    for cat in m.missing:
        print(f"    {cat}")
    if not m.missing:
        print("    (none)")
    print()
    for n in m.notes:
        print(f"  note: {n}")


def main(argv: list[str]) -> int:
    # Be graceful on legacy Windows consoles (cp437/cp1252): the summary uses a
    # few non-ASCII glyphs. Without this, a strict console can raise
    # UnicodeEncodeError and crash the intake step.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    input_dir = Path(argv[1]) if len(argv) > 1 else Path.cwd() / "bb-inputs"

    manifest = scan(input_dir)

    # Write the manifest next to the inputs so the triager/rebuttal can
    # reference stable paths and so re-runs are idempotent.
    manifest_path = input_dir / "manifest.json"
    manifest_path.write_text(json.dumps(asdict(manifest), indent=2))

    _print_summary(manifest)

    if any(manifest.ambiguous.values()):
        return 2
    if manifest.missing:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
