@echo off
REM Build Windows binary
cd /d "%~dp0.."
pip install pyinstaller
pyinstaller --onefile --name cathkb kb_tools/cli/main.py
echo Binary: dist\cathkb.exe
