# HackerOne report template

> Use for reports submitted to programs on **HackerOne**. Severity rating: CVSS (default v3.1; v4.0 is being adopted by some programs — verify with the specific program's policy page before submitting).

<!--
Severity labels on HackerOne map roughly to CVSS bands: Critical (9.0–10.0), High (7.0–8.9), Medium (4.0–6.9), Low (0.1–3.9), None/Informational (0.0). Use the platform's severity slider, not your own.
-->

## Title
<!-- Asset + vuln class + concrete impact. HackerOne rewards precise titles in triage. -->

## Asset type & URL
<!-- URL, parameter, or other asset identifier. Pick from: URL, Domain, Wildcard, API, Mobile App, Other. -->

## Severity
**Severity:** <Critical|High|Medium|Low|None>
**CVSS v3.1 vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`
**CVSS v3.1 base score:** <0.0–10.0>

<!-- If the program accepts v4.0, switch the prefix to CVSS:4.0/ and recompute. -->

## Weakness
<!-- CWE id, e.g. CWE-79 (XSS). HackerOne's structured-weakness picker will suggest; you can override with a custom weakness. -->

## Summary
<!-- 2–4 sentences. -->

## Steps to reproduce
<!-- Numbered, minimal, and verifiable from a clean state. -->
1.
2.
3.

## What is the expected behavior?
<!-- What *should* happen? -->

## What is the actual behavior?
<!-- What *does* happen? -->

## Demonstrated impact
<!-- Concrete. "Account takeover via session cookie exfiltration" beats "XSS." -->

## Suggested remediation
<!-- Concrete fix. -->

## Attachments / evidence
<!-- Screenshots, request/response captures, video PoC. Each claim must be backed by an attachment or an in-text capture. -->
