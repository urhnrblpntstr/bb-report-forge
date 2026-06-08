# bb-report-forge

A 3-agent bug-bounty report quality loop. Drops into any Claude Code project.

## What's in the bundle

```
bb-report-forge-bundle/
├── install.bat                 # Windows installer
├── install.sh                  # Linux / macOS / WSL installer
├── README.md                   # this file
└── .claude/
    ├── skills/
    │   └── bb-report-forge/    # the skill (SKILL.md, scripts, templates, reference, examples)
    └── agents/
        ├── triager.md          # adversarial reviewer (file-read only)
        └── rebuttal.md         # audit the triager (file-read only)
```

## Install

From the **target project's root**:

```bash
# Unix / Linux / macOS / WSL
/path/to/bb-report-forge-bundle/install.sh

# Windows (cmd or PowerShell)
D:\path\to\bb-report-forge-bundle\install.bat
```

The installer is **idempotent** — running it twice will not overwrite files that are already in place, so it's safe to run after pulling updates.

It does four things, in order:
1. Copies `.claude/skills/bb-report-forge/` into your project (skipped if already present).
2. Copies `.claude/agents/triager.md` and `rebuttal.md` into your project (skipped if already present).
3. Creates `bb-inputs/`, `bb-work/`, `bb-reports/` (skipped if already present).
4. Appends those three directories to `.gitignore` (skipped if already covered).

## Requirements

- **Claude Code** (any recent version). The skill installs as a project skill (`.claude/skills/`) and two subagents (`.claude/agents/`). The Hunter orchestrator invokes the `triager` and `rebuttal` agents **by name** via the Agent/Task tool — no extra wiring needed.
- **Python 3** (optional, recommended). Only the Phase 0 intake auto-evaluator (`scripts/scan_inputs.py`) uses it; it's pure standard library, no `pip install`. If `python` isn't on PATH, the skill tries `python3` / `py`, and if no interpreter exists it classifies the input files itself. The script also auto-creates `bb-inputs/` on first run instead of erroring, so a fresh project just works.

## Run

After install:

1. Drop your program's **scope**, **guidelines**, and (optionally) a **template** into `bb-inputs/`. Filenames don't matter; the auto-evaluator reads content + extension + filename hints.
2. Open a Claude Code session in the project root.
3. Invoke the skill: `/bb-report-forge`

The skill runs Phase 0 intake, asks you to confirm the resolved scope/guidelines/template paths, then drafts + triages + finalizes your findings.

## What it does

For each finding you bring it, the loop produces:

- A **polished report** filled into the platform template (HackerOne, Bugcrowd, Intigriti, YesWeHack, or generic).
- A **decision log** showing every triage → rebuttal → fix cycle, with grounded concerns and the rebuttal's classification of each.
- A **summary** with one row per finding: `ready` / `downgraded` / `withdrawn` + a one-line justification.

The system is honest by design. The Triager is an adversarial reviewer with a real triage-team mindset. The Rebuttal agrees with the Triager when the Triager is right. Out-of-scope or weak findings are downgraded or withdrawn, never inflated. Both agents are file-read only — they cannot generate fresh evidence to win an argument.

See `.claude/skills/bb-report-forge/SKILL.md` for the full spec and `.claude/skills/bb-report-forge/examples/worked-example/` for two worked examples (one solid finding that converges; one scanner-only flag that gets downgraded).

## What the skill does NOT do

- **It does not test targets.** The Hunter role (Main) assists the human; the human authorizes and performs all testing. The skill organizes and reasons about results.
- **It does not invent findings, impact, or scope.** Every claim in a final report must trace to evidence the hunter has on disk.
- **It does not weaken program guidelines.** If the program bans a vuln class or testing method, the report cannot include that class — the Triager will catch it.
- **It does not loop to invent work.** The stop conditions are explicit; the spec is `"Stop when there's nothing real left to do."`

## Customizing the platform default

The skill's built-in `DEFAULT_PLATFORM` is `generic`. To default to HackerOne (or any other platform) without dropping a custom template, set it in `SKILL.md`:

```yaml
DEFAULT_PLATFORM: hackerone
```

The user can still override per-finding.

## What works without internet

- The skill is fully offline.
- The intake auto-evaluator is pure-stdlib Python.
- The Triager and Rebuttal are file-read only.
- The Hunter role uses Read/Write/Edit/Glob/Grep; no network required for the report loop.

## Files of interest

| Path | Purpose |
|---|---|
| `.claude/skills/bb-report-forge/SKILL.md` | Main skill (orchestrator + Hunter role) |
| `.claude/agents/triager.md` | Adversarial reviewer. File-read only. |
| `.claude/agents/rebuttal.md` | Audits the triager. File-read only. |
| `.claude/skills/bb-report-forge/templates/` | `generic.md`, `hackerone.md`, `bugcrowd.md`, `intigriti.md`, `yeswehack.md` |
| `.claude/skills/bb-report-forge/reference/triage-rejection-codes.md` | Standard rejection codes shared by both agents |
| `.claude/skills/bb-report-forge/reference/severity-cvss-guide.md` | CVSS v3.1 + v4.0 cheat sheet, VRT note for Bugcrowd |
| `.claude/skills/bb-report-forge/reference/integrations.md` | Burp MCP config, recon-tool gating, evidence-verification gate |
| `.claude/skills/bb-report-forge/reference/intake-auto-evaluate.md` | Filename/extension/content rules used to classify `bb-inputs/` files |
| `.claude/skills/bb-report-forge/scripts/scan_inputs.py` | Pure-stdlib Python — runs the auto-evaluator, writes `bb-inputs/manifest.json` |
| `.claude/skills/bb-report-forge/examples/worked-example/` | Two fabricated findings: one ready, one downgraded |
