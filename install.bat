@echo off
REM bb-report-forge installer for Windows + Claude Code
REM
REM Usage (from the target project root, in cmd or PowerShell):
REM   D:\path\to\bb-report-forge-bundle\install.bat
REM
REM The project root is taken from the current working directory (the directory
REM you invoked the script from), NOT from the script's own location. The script
REM resolves its own location only to find the bundled files.
REM
REM What it does:
REM   1. Copies .claude\skills\bb-report-forge\ into <project>\.claude\skills\bb-report-forge\
REM   2. Copies .claude\agents\triager.md and rebuttal.md into <project>\.claude\agents\
REM   3. Creates bb-inputs\, bb-work\, bb-reports\ if they don't exist
REM   4. Appends gitignore entries for those dirs (if not already present)
REM
REM The installer is idempotent — files already present at the destination are
REM left in place. Use it to update too: re-run after pulling newer bundle
REM contents; only newly-added files will be installed.

setlocal
set "SCRIPT_DIR=%~dp0"
REM Strip trailing backslash from SCRIPT_DIR
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PROJECT_ROOT=%CD%"

echo.
echo bb-report-forge installer
echo Project root: %PROJECT_ROOT%
echo Bundle:       %SCRIPT_DIR%
echo.

REM Refuse to run if cwd is inside the bundle (would self-overwrite).
echo %PROJECT_ROOT% | findstr /B /I /C:"%SCRIPT_DIR%" >nul
if not errorlevel 1 (
    echo [err] You invoked install.bat from inside the bundle directory.
    echo        cd to the target project and re-run with the full bundle path:
    echo          cd C:\path\to\your-project
    echo          %SCRIPT_DIR%\install.bat
    exit /b 1
)

REM 1. Skill
if not exist "%PROJECT_ROOT%\.claude\skills\bb-report-forge\SKILL.md" (
    if exist "%SCRIPT_DIR%\.claude\skills\bb-report-forge\SKILL.md" (
        if not exist "%PROJECT_ROOT%\.claude\skills" mkdir "%PROJECT_ROOT%\.claude\skills"
        xcopy /E /I /Y "%SCRIPT_DIR%\.claude\skills\bb-report-forge" "%PROJECT_ROOT%\.claude\skills\bb-report-forge" >nul
        echo [ok] Installed .claude\skills\bb-report-forge\
    ) else (
        echo [err] Source .claude\skills\bb-report-forge\ not found next to install.bat
        exit /b 1
    )
) else (
    echo [skip] .claude\skills\bb-report-forge\ already exists at project root
)

REM 2. Agents
if not exist "%PROJECT_ROOT%\.claude\agents\triager.md" (
    if exist "%SCRIPT_DIR%\.claude\agents\triager.md" (
        if not exist "%PROJECT_ROOT%\.claude\agents" mkdir "%PROJECT_ROOT%\.claude\agents"
        copy /Y "%SCRIPT_DIR%\.claude\agents\triager.md"   "%PROJECT_ROOT%\.claude\agents\triager.md" >nul
        copy /Y "%SCRIPT_DIR%\.claude\agents\rebuttal.md"  "%PROJECT_ROOT%\.claude\agents\rebuttal.md" >nul
        echo [ok] Installed .claude\agents\{triager,rebuttal}.md
    ) else (
        echo [err] Source .claude\agents\ not found next to install.bat
        exit /b 1
    )
) else (
    echo [skip] .claude\agents\triager.md already exists at project root
)

REM 3. Working dirs
for %%D in (bb-inputs bb-work bb-reports) do (
    if not exist "%PROJECT_ROOT%\%%D" (
        mkdir "%PROJECT_ROOT%\%%D"
        echo [ok] Created %%D\
    ) else (
        echo [skip] %%D\ already exists
    )
)

REM 4. .gitignore
set "GI=%PROJECT_ROOT%\.gitignore"
set "NEED_GI=1"
if exist "%GI%" (
    findstr /B /C:"bb-inputs/" "%GI%" >nul 2>&1
    if not errorlevel 1 set "NEED_GI=0"
)
if "%NEED_GI%"=="1" (
    >> "%GI%" echo.
    >> "%GI%" echo # bb-report-forge working directories (do not commit scope or live evidence)
    >> "%GI%" echo bb-inputs/
    >> "%GI%" echo bb-work/
    >> "%GI%" echo bb-reports/
    echo [ok] Appended bb-inputs/, bb-work/, bb-reports/ to .gitignore
) else (
    echo [skip] .gitignore already covers bb-inputs/, bb-work/, bb-reports/
)

echo.
echo Install complete.
echo.
echo Next steps:
echo   1. Drop your program's scope, guidelines, and (optionally) template into bb-inputs\
echo   2. Open a Claude Code session in %PROJECT_ROOT%
echo   3. Invoke the skill:  /bb-report-forge
echo.
endlocal
