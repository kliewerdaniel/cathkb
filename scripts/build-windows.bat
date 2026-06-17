@echo off
REM Build Windows binary and NSIS installer
setlocal enabledelayedexpansion

set VERSION=%1
if "%VERSION%"=="" set VERSION=dev
set BINARY_NAME=cathkb
set BUILD_DIR=build\windows
set DIST_DIR=dist

echo === Building Windows binary ===

pip install pyinstaller
pyinstaller --onefile --name %BINARY_NAME% kb_tools\cli\main.py

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

copy "dist\%BINARY_NAME%.exe" "%BUILD_DIR%\%BINARY_NAME%.exe"

REM Bundle data if available
if exist "dist\cathkb-data.tar.gz" (
    copy "dist\cathkb-data.tar.gz" "%BUILD_DIR%\"
)

echo === Building NSIS installer ===

REM Check for NSIS
where makensis >nul 2>&1
if %errorlevel% equ 0 (
    makensis /DVERSION=%VERSION% /DBINARY_PATH=%BUILD_DIR%\%BINARY_NAME%.exe scripts\cathkb.nsi
    echo === Installer created: %DIST_DIR%\cathkb-%VERSION%-windows.exe ===
) else (
    echo === NSIS not found, skipping installer ===
    echo === Binary at: %BUILD_DIR%\%BINARY_NAME%.exe ===
    echo === Install NSIS: choco install nsis ===
)

endlocal
