# Bugcrowd report template

> Use for reports submitted to programs on **Bugcrowd**. Severity rating: **VRT (Vulnerability Rating Taxonomy) is primary; CVSS is alongside.** Bugcrowd triagers grade using VRT first and treat the CVSS vector as supporting evidence.

<!--
VRT basics: pick the most specific applicable variant. "P1" = critical (e.g. RCE, auth bypass on critical function). "P2" = high. "P3" = medium. "P4" = low. "P5" = informational. See Bugcrowd's VRT for the full tree and the impact-modifier rules.
-->

## Title
<!-- Asset + vuln class + (optional) impact. -->

## Target / asset
<!-- URL, host, or app identifier. Must be in scope. -->

## Vulnerability class
<!-- The closest VRT node, e.g. "Cross-Site Scripting (XSS) > Stored XSS > Stored XSS in a comment field." Be specific — the VRT node drives the priority. -->

## Severity
**Priority (VRT):** <P1|P2|P3|P4|P5>
**CVSS v3.1 vector (supporting):** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`
**CVSS v3.1 base score (supporting):** <0.0–10.0>

<!-- If VRT and CVSS disagree, VRT wins on Bugcrowd. Make sure the CVSS vector *supports* the VRT priority, doesn't fight it. -->

## Summary
<!-- 2–4 sentences. -->

## Reproduction steps
1.
2.
3.

## Proof of concept
<!-- Working PoC. URL, request, screenshot, or video. -->

## Impact
<!-- Concrete, not theoretical. -->

## Suggested remediation
<!-- Concrete fix. -->
