#!/usr/bin/env bash
# bb-report-forge installer for Unix-like systems (Linux, macOS, WSL)
#
# Usage (from the target project root):
#   /path/to/bb-report-forge-bundle/install.sh
#
# The project root is taken from the current working directory (the directory
# you invoked the script from), NOT from the script's own location. The script
# resolves its own location only to find the bundled files.
#
# What it does:
#   1. Copies .claude/skills/bb-report-forge/ into <project>/.claude/skills/bb-report-forge/
#   2. Copies .claude/agents/triager.md and rebuttal.md into <project>/.claude/agents/
#   3. Creates bb-inputs/, bb-work/, bb-reports/ if they don't exist
#   4. Appends gitignore entries for those dirs (if not already present)
#
# The installer is idempotent — files already present at the destination are
# left in place. Use it to update too: re-run after pulling newer bundle
# contents; only newly-added files will be installed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"

echo
echo "bb-report-forge installer"
echo "Project root: $PROJECT_ROOT"
echo "Bundle:       $SCRIPT_DIR"
echo

if [[ "$SCRIPT_DIR" == "$PROJECT_ROOT" || "$PROJECT_ROOT" == "$SCRIPT_DIR"/* ]]; then
    echo "[err] You invoked install.sh from inside the bundle directory."
    echo "       cd to the target project and re-run with the full bundle path:"
    echo "         cd /path/to/your-project"
    echo "         $SCRIPT_DIR/install.sh"
    exit 1
fi

# 1. Skill
if [[ ! -f "$PROJECT_ROOT/.claude/skills/bb-report-forge/SKILL.md" ]]; then
    if [[ -d "$SCRIPT_DIR/.claude/skills/bb-report-forge" ]]; then
        mkdir -p "$PROJECT_ROOT/.claude/skills"
        cp -R "$SCRIPT_DIR/.claude/skills/bb-report-forge" "$PROJECT_ROOT/.claude/skills/bb-report-forge"
        echo "[ok] Installed .claude/skills/bb-report-forge/"
    else
        echo "[err] Source .claude/skills/bb-report-forge/ not found next to install.sh"
        exit 1
    fi
else
    echo "[skip] .claude/skills/bb-report-forge/ already exists at project root"
fi

# 2. Agents
if [[ ! -f "$PROJECT_ROOT/.claude/agents/triager.md" ]]; then
    if [[ -d "$SCRIPT_DIR/.claude/agents" ]]; then
        mkdir -p "$PROJECT_ROOT/.claude/agents"
        cp "$SCRIPT_DIR/.claude/agents/triager.md"  "$PROJECT_ROOT/.claude/agents/triager.md"
        cp "$SCRIPT_DIR/.claude/agents/rebuttal.md" "$PROJECT_ROOT/.claude/agents/rebuttal.md"
        echo "[ok] Installed .claude/agents/{triager,rebuttal}.md"
    else
        echo "[err] Source .claude/agents/ not found next to install.sh"
        exit 1
    fi
else
    echo "[skip] .claude/agents/triager.md already exists at project root"
fi

# 3. Working dirs
for D in bb-inputs bb-work bb-reports; do
    if [[ ! -d "$PROJECT_ROOT/$D" ]]; then
        mkdir "$PROJECT_ROOT/$D"
        echo "[ok] Created $D/"
    else
        echo "[skip] $D/ already exists"
    fi
done

# 4. .gitignore
GI="$PROJECT_ROOT/.gitignore"
NEED_GI=1
if [[ -f "$GI" ]] && grep -qE '^bb-inputs/' "$GI"; then
    NEED_GI=0
fi
if [[ "$NEED_GI" -eq 1 ]]; then
    {
        echo
        echo "# bb-report-forge working directories (do not commit scope or live evidence)"
        echo "bb-inputs/"
        echo "bb-work/"
        echo "bb-reports/"
    } >> "$GI"
    echo "[ok] Appended bb-inputs/, bb-work/, bb-reports/ to .gitignore"
else
    echo "[skip] .gitignore already covers bb-inputs/, bb-work/, bb-reports/"
fi

echo
echo "Install complete."
echo
echo "Next steps:"
echo "  1. Drop your program's scope, guidelines, and (optionally) template into bb-inputs/"
echo "  2. Open a Claude Code session in $PROJECT_ROOT"
echo "  3. Invoke the skill:  /bb-report-forge"
echo
