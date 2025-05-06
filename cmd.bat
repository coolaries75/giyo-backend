@echo off
:: Absolute protection against infinite loops
if defined _CMD_OPENED exit /b
set "_CMD_OPENED=1"

:: Get the script directory safely
set "script_dir=%~dp0"
set "script_dir=%script_dir:~0,-1%"

:: Open exactly one CMD window with clean environment
start "" cmd /E:OFF /D /K "(
    cd /d "%script_dir%"
    title CMD in %script_dir:~0,15%...
    echo Ready in: %script_dir%
    set "_CMD_OPENED="
)"

:: Immediately exit the launching window
exit