# Integrations — Burp MCP, recon tools, evidence gate

> The skill runs end-to-end **without** any of this. Integrations are opt-in and live only in the intake / hunt / verify phases. The adversarial review (Triager + Rebuttal) never touches any of them.

## Per-agent tool policy (the load-bearing rule)

| Role | Tool allow-list | What this means in practice |
|---|---|---|
| **Main / Hunter** (the skill) | Full filesystem + optional MCP (Burp, gated recon) | Only role that can gather new evidence. |
| **Triager** (`AGENTS_PATH/triager.md`) | `Read`, `Glob`, `Grep` | No shell, no network, no MCP, no writes. |
| **Rebuttal** (`AGENTS_PATH/rebuttal.md`) | `Read`, `Glob`, `Grep` | No shell, no network, no MCP, no writes. |

The allow-list is the real enforcement: every unlisted tool is denied by omission. The Triager and Rebuttal judge what is on the page against scope + captured evidence; they cannot generate fresh evidence to support or attack a claim. This separation is what stops the loop from manufacturing "evidence" to win an argument.

**Honest limit:** frontmatter cannot path-restrict `Read`. "Read only within `bb-inputs/` and `bb-work/`" is a system-prompt rule on the two reviewers, not a permission rule. The denials that matter — no shell, no network, no MCP, no writes — are hard.

## 7b. Evidence layer — Burp Suite MCP

The official PortSwigger Burp Suite MCP extension exposes proxy history and request/response manipulation. Use it as the evidence backbone: every report claim anchors to a real captured exchange.

**Install:**
1. In Burp Suite → Extender → BApp Store → install **"MCP Server for Burp Suite"** (the official PortSwigger one).
2. Enable the extension. Confirm the listening port (default `9876`).
3. Grant the `burp` MCP server **to the Hunter agent only** — not to the Triager or the Rebuttal.

**Project-level `.mcp.json` (drop at repo root):**

```json
{
  "mcpServers": {
    "burp": { "type": "sse", "url": "http://127.0.0.1:9876/sse" }
  }
}
```

If you run Burp on a different host/port, change the URL. If you use stdio transport, change `"type": "stdio"` and add `"command"`/`"args"`.

**Heavier community servers** (e.g. BurpMCP-Ultra) are optional and only if you explicitly opt in and trust the source. An MCP server runs with real capability locally — treat it like installing any other tool.

## 7c. Discovery layer — autonomous recon (gated)

The Hunter may consume candidate findings from an autonomous recon MCP (e.g. HexStrike-class servers running nmap / nuclei / ffuf / sqlmap / etc.). Treat all such output as **unverified candidates**, never report-ready. Four mandatory gates:

### 1. Scope gate
Every target/asset is checked against the uploaded `bb-inputs/scope.md` *and* the program's testing rules. Many programs forbid automated scanning — that is a guideline-compliance fail, not just a scope fail. Out-of-scope or rules-violating calls are **blocked and logged**, not silently skipped.

### 2. Authorization gate
The user must explicitly confirm they are authorized to run automated tooling against the targets for this specific program. A blanket "I have authorization for this program" does not cover automated scanning if the program forbids it.

### 3. Trust gate
Pin recon MCP servers to a reviewed version/source. An MCP server runs with real capability locally. Prefer first-party/official servers; flag forks.

### 4. Verification gate (the load-bearing one)
A candidate from any automated tool **cannot reach `ready`** until its reproduction steps are reproduced and captured manually (ideally via the Burp evidence layer). "Scanner flagged it" is explicitly insufficient — the Triager will reject it as `insufficient-evidence`. This is the gate that distinguishes a real bug from a false positive that matches a regex.

## 7d. Graceful degradation

If no MCP tools are connected, the skill runs in **manual mode**: the Hunter works from evidence the user pastes/uploads, and the verification gate is satisfied by user-provided request/response captures. Never block the workflow on an absent integration; never assume a tool's output exists if the tool wasn't actually run.

## Worked evidence — what a "captured exchange" looks like

When the Hunter reports a finding, the evidence section should include something like:

```http
POST /api/comments HTTP/1.1
Host: demo.example.com
Content-Type: application/json
Cookie: session=<redacted>

{"body": "<img src=x onerror=alert(1)>"}
```

```http
HTTP/1.1 201 Created
Content-Type: text/html; charset=utf-8

{"id": 4242, "body": "<img src=x onerror=alert(1)>", "author": "victim"}
```

Followed by a second request from a different session that retrieves the comment and a screenshot/PoC video showing the alert firing. That is what "evidence" means in this skill — not a sentence in a paragraph.

## Anti-pattern: the loop manufacturing evidence

If, mid-loop, the Hunter adds a new piece of evidence that was not in the original `bb-work/<finding-id>/raw-evidence/` directory, and that new evidence is what makes the rebuttal's `INVALID` classification land — that is the loop cheating. The Triager and Rebuttal are not allowed to generate evidence. The Hunter is. But new Hunter evidence must be **declared and logged** in the decision log: "Cycle 2: Hunter added a manual reproduction capture to `evidence/cycle-2-manual-repro.md`." Hidden evidence is the failure mode this whole architecture is designed to prevent.
