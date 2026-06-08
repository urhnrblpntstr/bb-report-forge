# Triage rejection codes

> Standard rejection codes used by the Triager and the Rebuttal. Both agents map their concerns to these. Keep this list short and stable — programs add their own program-specific rules, but the *category* of rejection comes from this set.

| Code | One-line definition |
|---|---|
| `out-of-scope` | The affected asset, vuln class, or test method is not permitted by the program policy. |
| `no-impact` | No demonstrated security or business impact; the issue is cosmetic or unactionable. |
| `theoretical` | Possible in principle but not demonstrated; no working PoC; conditions not realizable in the program's threat model. |
| `not-reproducible` | The steps do not work as written from a clean state, or they require knowledge only the author has. |
| `best-practice` | A hardening note, missing header, or generic advice with no concrete security impact. |
| `duplicate` | Same root cause as a previously reported or documented issue, including "accepted risk" disclosures. |
| `informational` | True observation, but the program explicitly does not pay for this category. |
| `out-of-threat-model` | Exploitation requires conditions the program does not defend against (MITM, physical access, victim self-XSS, etc.). |
| `insufficient-evidence` | Claims are not backed by request/response captures, screenshots, or a reproducible PoC. Scanner flags without a manual reproduction land here. |

## How the agents use these

- **Triager** lists every `rejection_reasons[]` code that applies. Multiple codes can apply to one finding (e.g. `out-of-scope` + `insufficient-evidence`).
- **Rebuttal** classifies each triager concern as `VALID` / `PARTIALLY-VALID` / `INVALID` / `FINDING-NOT-VIABLE`. A `FINDING-NOT-VIABLE` classification is the rebuttal's signal that the finding should be `downgrade`d or `withdraw`n — it must cite one of the codes above or the specific scope/guideline line.
- **Main** uses the final recommendation to write the one-line justification in `OUTPUT_DIR/summary.md`.

## Notes for the hunter

- A finding can be salvageable from one rejection code and fatal under another. Example: a scanner flag with no PoC is `insufficient-evidence` (fixable by reproducing manually) but if the same finding is on an out-of-scope asset, it is `out-of-scope` (not fixable).
- Do not patch a finding by reclassifying it. The classification comes from the evidence, not the desired outcome.
