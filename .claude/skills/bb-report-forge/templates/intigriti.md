# Intigriti report template

> Use for reports submitted to programs on **Intigriti**. Severity rating: CVSS (default v3.1). Intigriti uses a 5-step severity scale (Critical / High / Medium / Low / Informational) with CVSS bands similar to HackerOne.

<!--
Intigriti specifics:
- "Critical" requires proven, reproducible impact on a critical asset (auth bypass, RCE, sensitive data exposure at scale).
- "Informational" is the right home for missing headers, best-practice, self-XSS, and unproven-theoretical findings. Do not inflate.
- Many Intigriti programs forbid automated scanning — check the program rules before using recon tools.
-->

## Title
<!-- Asset + vuln class + impact. -->

## Target
<!-- URL, parameter, or asset. -->

## Severity
**Severity:** <Critical|High|Medium|Low|Informational>
**CVSS v3.1 vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`
**CVSS v3.1 base score:** <0.0–10.0>

## Vulnerability description
<!-- 2–4 sentence summary. -->

## Steps to reproduce
1.
2.
3.

## Impact
<!-- Concrete. -->

## Evidence
<!-- HTTP request/response, screenshots, video. -->

## Suggested fix
<!-- Concrete remediation. -->
