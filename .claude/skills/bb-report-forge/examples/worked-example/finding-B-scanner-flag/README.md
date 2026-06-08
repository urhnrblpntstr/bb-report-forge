---
name: bb-report-forge example — Finding B (scanner flag, downgraded)
description: Fabricated but realistic example showing the verification gate firing: a scanner-flagged candidate with no manual reproduction is downgraded for insufficient evidence.
metadata:
  type: example
  outcome: downgraded
  cycles: 2
---

# Example B — Scanner-flagged candidate downgraded

## Inputs (hypothetical, fabricated)

**Scope:** same as Example A.
**Guidelines, additional clause:** "Reports based solely on automated scanner output, with no manual reproduction, will be closed as Informational."

**Raw candidate (`bb-work/finding-B-scanner-flag/raw-evidence/scanner-output.txt`):**
- Source: a recon MCP (nuclei template `http/misconfiguration/x-debug-header`)
- Output: `https://demo.example.com/api/health` responds with header `X-Debug: true` on a `200 OK`.
- No manual reproduction attempt captured. No demonstration that the header is reachable from an unprivileged user, no demonstration of any side effect of the header, no proof that the program cares about debug headers.

## Cycle 1

**Triager verdict (excerpt):**
```yaml
verdict: reject
likely_severity: Informational
concerns:
  - id: C1
    category: evidence-sufficiency
    severity_of_concern: blocking
    grounding: "bb-work/finding-B-scanner-flag/raw-evidence/scanner-output.txt contains only scanner output. No manual reproduction capture, no request/response pair from a clean state, no screenshot."
    what_would_fix_it: "Manually reproduce: send a clean GET /api/health from a fresh session, capture the response, and demonstrate an actual impact of the X-Debug header (or argue why the program should care about a non-impactful header)."
  - id: C2
    category: demonstrated-impact
    severity_of_concern: blocking
    grounding: "draft.md 'Impact' section is empty. A debug header with no demonstrated side effect is best-practice/informational, not a security finding."
    what_would_fix_it: "Either demonstrate an actual impact (e.g. the header enables a hidden endpoint that leaks data) or accept the finding is Informational."
rejection_reasons:
  - insufficient-evidence
  - no-impact
```

**Rebuttal classification (excerpt):**
```yaml
per_concern:
  - concern_id: C1
    classification: VALID
    reasoning: "Triager is right. The program explicitly closes scanner-only reports as Informational. This is the verification gate firing as designed."
    evidence_pointer_or_required_work: "Obtain a manual reproduction capture from a clean state, or accept the downgrade."
  - concern_id: C2
    classification: VALID
    reasoning: "Triager is right. No impact is demonstrated. A non-impactful debug header is best-practice, not a security finding."
    evidence_pointer_or_required_work: "Same as C1 — manual reproduction is the only path forward; absent that, the finding has no demonstrated impact."
recommendation: downgrade
action_items:
  - { order: 1, tag: drop-finding, description: "Downgrade to Informational; one confirming cycle runs." }
```

**Main applies.** Finding is now marked `Informational`. Cycle 1 hash differs from cycle 0 → loop continues for the confirming cycle.

## Cycle 2 (confirmation)

**Triager verdict:**
```yaml
verdict: accept
likely_severity: Informational
concerns: []
rejection_reasons: []
notes: "Downgrade to Informational is consistent with program guidelines and the absence of demonstrated impact. No grounded concerns."
```

**Rebuttal recommendation:** `finalize`.

**Converged.** `downgraded` to Informational.

## Final state

- Status: `downgraded`
- Justification (for `summary.md`): "Scanner-flagged X-Debug header with no manual reproduction and no demonstrated impact. Downgraded to Informational per program guideline closing scanner-only reports."
- Decision log: 4 entries (cycle 1 init, cycle 1 actions, cycle 2 confirm, finalize).

## What this example proves

1. The verification gate fires as designed — a scanner flag with no manual reproduction cannot reach `ready`.
2. The Triager cited the **program's own guideline** ("scanner-only reports → Informational") as the rejection grounds, not a generic standard. This is what grounded concerns look like.
3. The rebuttal **agreed with the triager again** — proof the system is not biased toward preserving findings.
4. The hunter can still submit the finding as Informational. The skill did not silently kill the report; it accurately classified it and put it on the right shelf.
5. The Hunter is invited (via the action item) to do the manual reproduction and re-enter the loop with a stronger finding — the system degrades gracefully instead of punishing the hunter.
