# Intake auto-evaluator

> The Phase 0 step that scans `bb-inputs/` and decides which file is scope, which is guidelines, and which is template — without requiring exact filenames. The skill uses this on every invocation, before doing anything else.

## Why this exists

Programs export scope and guidelines in many forms: a `scope.md`, a `wildcards.csv`, a `policy.pdf`, a `domain-list.txt`, a `guideline.md` (no `s`), a `tempalate.md` (typo). The skill used to require exact filenames and the user had to rename things to fit. That is friction with no upside — the *content* of a file tells you what it is, the *name* is a hint at best.

The auto-evaluator:

1. Lists every file in `bb-inputs/` (top level only)
2. Scores each file against per-category regex fingerprints
3. Boosts the score with filename hints and extension hints
4. Picks the highest-scoring candidate per category
5. Writes a `bb-inputs/manifest.json` recording the decision
6. Asks the user when it is genuinely uncertain — never guesses

## How to run

From the project root, after the user has dropped files into `bb-inputs/`:

```bash
python .claude/skills/bb-report-forge/scripts/scan_inputs.py
```

Or point it at any directory:

```bash
python .claude/skills/bb-report-forge/scripts/scan_inputs.py /path/to/bb-inputs
```

The script writes `bb-inputs/manifest.json` and prints a summary. Exit codes:

| Code | Meaning | What the skill does |
|---|---|---|
| `0` | All three categories resolved | Proceed to Phase 1 |
| `2` | At least one category is ambiguous (2+ candidates tied) | Ask the user to pick |
| `3` | At least one category has zero candidates | Ask the user to drop a file |

## What the script recognizes

### Filename hints (boost a category's score by 5)

A basename is split on `-`, `_`, and whitespace. A category gets a +5 boost if any segment matches one of its hints:

| Category | Hints (substring match) |
|---|---|
| `scope` | `scope`, `targets`, `wildcards`, `in-scope`, `inscope`, `assets`, `domains` |
| `guidelines` | `guideline`, `guidelines`, `policy`, `policies`, `rules`, `testing-rules`, `rules-of-engagement`, `roe`, `disclosure`, `bounty` |
| `template` | `template`, `tempalate` (typo), `templete` (typo), `report-template`, `submission` |

A file named `telescope.md` does **not** match the `scope` hint because `scope` is not its own segment. False positives here would be embarrassing.

### Extension hints (boost a category's score by 3)

| Category | Extensions |
|---|---|
| `scope` | `.csv`, `.tsv`, `.txt`, `.json`, `.yaml`, `.yml` |
| `guidelines` | `.md`, `.txt`, `.pdf` |
| `template` | `.md`, `.txt`, `.html` |

PDFs are extension-hinted but not content-fingerprinted (binary). The skill surfaces that as a "we cannot read this — please confirm" note.

### Content fingerprints (boost a category's score by 1 per match)

Conservative regex patterns. The full list is in the script. Highlights:

| Category | Patterns |
|---|---|
| `scope` | `in-scope`, `out-of-scope`, `excluded`, `wildcard(s)`, `assets`, `*.example.com`-style host patterns |
| `guidelines` | `guideline(s)`, `rules of engagement`, `responsible disclosure`, `don't test`, `bounty`, `90-day`, `severity:` |
| `template` | `# title`, `## severity`, `## cvss`, `## asset`, `## summary`, `## reproduction`, `## impact`, `## remediation` headings; `CVSS` string; HTML comments |

A file with all the template headings scores +6 on `template` and likely 0 on the others — clean win. A file that says "scope" once and "policy" twice will land as ambiguous and the user will be asked.

## Triage rules

The script picks the **highest combined score** per file. Combined score = `max(filename_hint, 0) * 5 + max(extension_hint, 0) * 3 + content_matches`.

A file is flagged **ambiguous** if:

- Its top-2 categories differ by ≤ 2 points (e.g. scope=8, guidelines=7), **or**
- 2+ files in the same directory both want to be the same category with similar confidence

When a category is ambiguous, the skill does **not** guess. It shows the user the candidate paths and asks which is which. This is principle 2 ("Scope is law") in action — better to ask once than to silently misclassify a scope file as guidelines.

## Manifest schema

`bb-inputs/manifest.json` looks like:

```json
{
  "generated_at": "2026-06-07T18:50:00Z",
  "input_dir": "/path/to/bb-inputs",
  "files": [
    {
      "path": "/path/to/bb-inputs/scope.md",
      "relpath": "scope.md",
      "basename": "scope.md",
      "extension": ".md",
      "size_bytes": 1834,
      "content_sha256": "a1b2c3d4e5f6...",
      "extension_hint": "guidelines",
      "filename_hint": "scope",
      "content_scores": {"scope": 6, "guidelines": 1, "template": 0},
      "final_category": "scope",
      "confidence": 1.0,
      "ambiguous_with": []
    }
  ],
  "resolved": {
    "scope": "scope.md",
    "guidelines": "guidelines.md",
    "template": "template.md"
  },
  "ambiguous": {
    "scope": [],
    "guidelines": [],
    "template": []
  },
  "missing": [],
  "notes": []
}
```

The triager and rebuttal agents do **not** read `manifest.json` directly (their tool allow-list is `Read, Glob, Grep` and they shouldn't trust a generated file). The Main / Hunter reads it and passes the resolved paths to the triager as part of the per-cycle prompt. This keeps the manifest out of the trust boundary.

## Examples the script handles correctly

| Dropped files | Resolution |
|---|---|
| `scope.md`, `guidelines.md`, `template.md` | All resolved, exit 0 |
| `scope.md`, `guideline.md` (no `s`), `template.md` | All resolved — `guideline` matches the guidelines hint via singular form |
| `wildcards.csv`, `policy.md`, `tempalate.md` | All resolved — extension hint catches CSV, filename hint catches `policy` and `tempalate` |
| `targets.csv`, `README.md` (no `s`) | Scope → `targets.csv`; guidelines → ask (README is too generic); template → missing → ask |
| `scope.md`, `scope-v2.md` | Ambiguous → ask the user which is canonical; the other gets moved to `bb-inputs/_unmatched/` |
| `policy.pdf` | Extension-hinted as guidelines; content unreadable → ask the user to confirm |
| Empty `bb-inputs/` | Missing all three → ask the user to drop at least scope and guidelines |

## What this does not do

- **It does not read subdirectories.** `bb-inputs/scope/wildcards.csv` is not auto-found. Most hunters drop everything at the top level, and scanning recursively invites matching files the user did not intend.
- **It does not dedupe by content.** A copy of `scope.md` named `scope-backup.md` will both score as scope and the script will ask which is canonical.
- **It does not write to the input files.** It only writes `bb-inputs/manifest.json`.
- **It does not invent scope.** If a category cannot be resolved, the skill asks the user — it never proceeds on assumed scope.

## Updating the hints

If you find a real program that exports scope in a form the hints don't catch, add it to `FILENAME_HINTS` and `SCOPE_PATTERNS` in the script. Keep the additions conservative — false positives here lead the triager to review the wrong file, which is a real failure mode.
