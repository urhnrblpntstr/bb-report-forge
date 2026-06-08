# Severity & CVSS guide

> Concise discipline guide for severity claims. The Triager rejects inflated vectors; the Rebuttal audits those rejections. This is the shared reference.

## Default per platform

| Platform | Primary | Notes |
|---|---|---|
| HackerOne | CVSS v3.1 (v4.0 migrating) | Use the platform's severity slider; CVSS supports. |
| Bugcrowd | **VRT** | VRT is primary; CVSS alongside. |
| Intigriti | CVSS v3.1 | Program-specific reward tables vary. |
| YesWeHack | CVSS v3.1 | Cite the program's scope rewards table. |
| Generic | CVSS v3.1 | Default. |

If a program has explicitly migrated to CVSS v4.0, switch the vector prefix to `CVSS:4.0/` and recompute. Verify on the program page before submitting.

## CVSS v3.1 quick reference

The eight base metrics. Each must be defensible against the actual evidence.

| Metric | Values | What to pick, and why |
|---|---|---|
| **AV** (Attack Vector) | `N`etwork / `A`djacent / `L`ocal / `P`hysical | Web app reached over the internet = `N`. Same physical subnet = `A`. Local shell = `L`. |
| **AC** (Attack Complexity) | `L`ow / `H`igh | `L` if no special conditions; `H` if the attacker must win a race or evade a known-mitigated condition. |
| **PR** (Privileges Required) | `N`one / `L`ow / `H`igh | `N` if unauthenticated; `L` if a normal user; `H` if admin. Scope (`S`) flips with PR. |
| **UI** (User Interaction) | `N`one / `R`equired | XSS, CSRF = `R`. Direct injection with no victim = `N`. |
| **S** (Scope) | `U`nchanged / `C`hanged | `C` only if exploitation crosses a security authority boundary (e.g. XSS reading admin-only data). Most web vulns are `U`. |
| **C** (Confidentiality) | `N`one / `L`ow / `H`igh | What can the attacker actually read? |
| **I** (Integrity) | `N`one / `L`ow / `H`igh | What can the attacker actually write/modify? |
| **A** (Availability) | `N`one / `L`ow / `H`igh | What can the attacker actually break? |

**Score bands (v3.1):** None 0.0 · Low 0.1–3.9 · Medium 4.0–6.9 · High 7.0–8.9 · Critical 9.0–10.0.

Compute at <https://www.first.org/cvss/calculator/3.1>. Do not invent scores.

## CVSS v4.0 quick reference (for migrating programs)

v4.0 splits the legacy CIA into four impact metrics (VC, VI, VA, SC, SI, SA) and adds `AT` (Attack Requirements) and `E` (subsequent system impact). v4.0 also adds `CR`/`IR`/`AR` (Confidentiality, Integrity, Availability Requirements) for environmental context. The official calculator is at <https://www.first.org/cvss/calculator/4.0>.

**If you are not sure which version the program uses, default to v3.1.** The Triager will flag a v4.0 vector on a v3.1 program as a minor concern, not a blocker.

## Common inflation traps (the Triager will flag these)

- **`S:C` on a single-origin web app.** Scope-Changed requires crossing a security authority. Reading another user's data on the same origin is not Scope-Changed unless the data lives in a separate trust boundary.
- **`C:H / I:H / A:H` for a finding that only leaks a non-sensitive token.** Lower the C and I, lower the score.
- **`UI:N` on stored XSS.** Reflected/stored XSS almost always requires a victim. Default to `UI:R`.
- **`AV:N` on a localhost-only app.** Should be `AV:L`.
- **`PR:N` on a finding that requires authentication.** Should be `PR:L` (or `PR:H` if admin).
- **`AC:L` when the attack requires a race condition or an exotic race window.** Should be `AC:H`.

## Bugcrowd VRT note (one paragraph)

VRT (Vulnerability Rating Taxonomy) is a tree of vuln classes with assigned priorities. Pick the **most specific applicable node** — "Stored XSS in a comment field" is a different node from "Reflected XSS." The priority is the priority of the *node*, modulated by demonstrated impact (e.g. account takeover bumps the priority). VRT disagreements with your CVSS vector are resolved in VRT's favor on Bugcrowd. The full VRT is at <https://bugcrowd.com/vulnerability-rating-taxonomy>.

## Self-check before you claim a severity

Ask: *"If the Triager reads my report cold, with no prior context, can they point to a specific line in my evidence that supports each metric?"* If you cannot, lower the metric, lower the score, or get more evidence.
