@echo off
setlocal enabledelayedexpansion


:: Get current folder name
for %%a in (.) do set "FOLDER_NAME=%%~nxa"
if "%FOLDER_NAME%"=="." set "FOLDER_NAME=root"

:: Prepare output filename
set OUTPUT_FILE=%OUTPUT_PREFIX%%FOLDER_NAME%.txt

:: Check if file exists and rename with timestamp if needed
if exist "%OUTPUT_FILE%" (
    for /f "tokens=1-6 delims=/: " %%a in ("%date% %time%") do (
        set TIMESTAMP=%%a-%%b-%%c-%%d-%%e
        set TIMESTAMP=!TIMESTAMP: =0!
    )
    set TIMESTAMP=%TIMESTAMP:~0,2%-%TIMESTAMP:~3,2%-%TIMESTAMP:~6,2%-%TIMESTAMP:~9,2%-%TIMESTAMP:~12,2%
    ren "%OUTPUT_FILE%" "%OUTPUT_PREFIX%%FOLDER_NAME%_%TIMESTAMP%.txt"
)

:: Main path generation
(
    echo Directory listing for: %~dp0
    echo.
    call :listPaths "." ""
) > "%OUTPUT_FILE%"

echo Directory and file paths saved to %OUTPUT_FILE%
goto :eof

:listPaths
setlocal
set "current_dir=%~1"
set "parent_path=%~2"

:: Process files first
for %%f in ("%current_dir%\*.*") do (
    set "file_name=%%~nxf"
    if not "!file_name!"=="%~nx0" (
        echo %~dp0!parent_path:~1!\!file_name!
    )
)

:: Then process directories
for /d %%d in ("%current_dir%\*") do (
    set "dir_name=%%~nxd"
    set "full_path=%parent_path%\!dir_name!"
    set "exclude=0"
    
    :: Check if directory should be excluded
    for %%x in (%EXCLUDE_DIRS%) do (
        if /i "!dir_name!"=="%%x" set "exclude=1"
    )
    
    if !exclude!==0 (
        echo %~dp0!full_path:~1!\
        call :listPaths "%%d" "!full_path!"
    )
)
endlocal
goto :eof