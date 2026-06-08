---
name: bb-report-forge example — Finding A (solid stored XSS, converges)
description: Fabricated but realistic example showing the full triage → rebuttal → fix → finalize loop on a finding that survives.
metadata:
  type: example
  outcome: ready
  cycles: 2
---

# Example A — Stored XSS in comment field converges in 2 cycles

## Inputs (hypothetical, fabricated)

**Scope (`bb-inputs/scope.md`, excerpt):**
> In scope: `https://demo.example.com/*` — all web application vulnerabilities. Out of scope: `*.marketing.example.com`, third-party widgets, volumetric DoS.

**Guidelines (`bb-inputs/guidelines.md`, excerpt):**
> Test your own accounts only. Manual testing is encouraged; please refrain from automated scanners. XSS is in scope.

**Raw evidence (`bb-work/finding-A-stored-xss/raw-evidence/cycle-0-repro.txt`):**
- Request 1: victim session `POST /api/comments` with `{"body":"<img src=x onerror=alert(1)>"}` → `201 Created`
- Request 2: attacker session `GET /posts/42` — body contains the unsanitized comment; PoC video shows `alert(1)` firing in the attacker's session.

## Cycle 1

**Triager verdict (excerpt):**
```yaml
verdict: needs-info
likely_severity: High
concerns:
  - id: C1
    category: severity-cvss
    severity_of_concern: minor
    grounding: "draft.md CVSS vector uses AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N — Scope:Unchanged is correct for same-origin read, but the impact statement claims 'account takeover' which would justify S:C."
    what_would_fix_it: "Either narrow the impact statement to 'session cookie theft in victim's session' and keep S:U, or provide a second capture showing the cookie is exfiltrated to a separate origin and bump to S:C."
  - id: C2
    category: evidence-sufficiency
    severity_of_concern: major
    grounding: "draft.md 'Evidence' section references a video but no path is given."
    what_would_fix_it: "Add the path: 'evidence/cycle-0-repro.txt' with the second-session capture and a one-line note describing the video."
```

**Rebuttal classification (excerpt):**
```yaml
per_concern:
  - concern_id: C1
    classification: VALID
    reasoning: "Triager is right. The impact statement overreaches vs. the vector. Fix the impact, keep S:U."
    evidence_pointer_or_required_work: "Replace 'account takeover' with 'attacker executes JavaScript in the victim's session and can read the session cookie via document.cookie, leading to session hijack if the cookie is non-HttpOnly.'"
  - concern_id: C2
    classification: VALID
    reasoning: "Triager is right. Path is missing."
    evidence_pointer_or_required_work: "Add: 'See bb-work/finding-A-stored-xss/raw-evidence/cycle-0-repro.txt for both captures.'"
recommendation: revise
action_items:
  - { order: 1, tag: fix-text,     description: "Narrow impact statement per C1." }
  - { order: 2, tag: add-evidence, description: "Cite the evidence path per C2." }
```

**Main applies both.** Cycle 1 hash differs from cycle 0 → loop continues.

## Cycle 2

**Triager verdict:**
```yaml
verdict: accept
likely_severity: High
concerns: []
rejection_reasons: []
notes: "Impact is now internally consistent with S:U; evidence path is cited. No grounded concerns remaining."
```

**Rebuttal recommendation:**
```yaml
recommendation: finalize
action_items: []
```

**Converged.** Hash unchanged across a confirmation check → `ready`.

## Final state

- Status: `ready`
- Justification (for `summary.md`): "Stored XSS in `/api/comments` body, executes in viewer's session. Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N → 7.4 (High). Converged in 2 cycles; no open concerns."
- Decision log: see `bb-work/finding-A-stored-xss/decision-log.md` (4 entries: cycle 1 init, cycle 1 actions, cycle 2 verdict, finalize).

## What this example proves

1. The Triager raised two **grounded** concerns (vector↔impact mismatch, missing evidence path). Both are real and the rebuttal agreed.
2. The rebuttal **agreed with the triager** on both concerns. This is the design — the rebuttal is not a blind defender.
3. The fix was a text edit + a path citation, not new evidence. The cycle 1 evidence was already sufficient; only the report's *narrative* was off.
4. Convergence happened in 2 cycles, well under `MAX_ITERATIONS: 5`.
