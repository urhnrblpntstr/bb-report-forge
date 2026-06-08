# Generic bug-bounty report template

> Default template when the platform is unknown or unspecified. Uses CVSS v3.1 by default. Bugcrowd-style programs should use `bugcrowd.md` instead (VRT primary).

<!--
Severity defaults: Critical / High / Medium / Low / Informational
CVSS default: v3.1. To use v4.0, replace the vector and recompute the base score.
Platform mapping: this template is for programs on platforms without a custom template, or for offline/internal triage.
-->

## Title
<!-- One-line, asset + vuln class + (optional) impact. Example: "Stored XSS in /comments allows account takeover via session cookie theft" -->

## Severity
<!-- Critical | High | Medium | Low | Informational -->
**Severity:** <Critical|High|Medium|Low|Informational>
**CVSS v3.1 vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`
**CVSS v3.1 base score:** <0.0–10.0>

<!--
Reminder: the vector must be internally consistent. AV:N + UI:R is normal for XSS; AV:L is wrong for a web app finding. If you can't justify a metric, leave it at the default and downrate severity.
-->

## Affected asset(s)
<!-- URLs, hosts, parameters. Must all be in scope per INPUTS_DIR/scope.md. -->

## Summary
<!-- 2–4 sentences. What is the bug, where, and what's the impact? -->

## Reproduction steps
<!-- Numbered. Must work as written, from a clean state, by someone who isn't the author. -->
1.
2.
3.

## Demonstrated impact
<!-- What can an attacker actually do? Be specific. "Account takeover" beats "session hijack is possible" beats "XSS exists." -->

## Evidence
<!-- Paste the relevant HTTP request/response, attach screenshots, link the PoC video. Every claim above must trace to evidence here. -->
- Request:
  ```http
  GET / HTTP/1.1
  Host: example.com
  ```
- Response (relevant excerpt):
  ```http
  HTTP/1.1 200 OK
  ...
  ```
- Screenshot / log / capture: `<path or "see attached">`

## Remediation
<!-- Concrete fix. Specific, not "sanitize input." -->

## References
<!-- CVE, CWE, vendor advisory, OWASP page — any external anchor that helps the triager. -->
