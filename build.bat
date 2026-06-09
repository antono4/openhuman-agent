@echo off
REM Build script for OpenHuman AI Agent (Windows)

echo Building OpenHuman AI Agent...

REM Install dependencies if needed
pip install pyinstaller -q

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
pyinstaller openhuman.spec --clean

REM Create output directory
if not exist release mkdir release

REM Copy executable
xcopy /s /e /y dist\openhuman-agent release\openhuman-agent\

REM Create README for release
echo OpenHuman AI Agent > release\README.txt
echo ================== >> release\README.txt
echo. >> release\README.txt
echo Usage: >> release\README.txt
echo   openhuman-agent.exe agent list    - List available agents >> release\README.txt
echo   openhuman-agent.exe agent show    - Show agent definition >> release\README.txt
echo   openhuman-agent.exe skill list    - List available skills >> release\README.txt
echo   openhuman-agent.exe skill run     - Execute a skill >> release\README.txt
echo   openhuman-agent.exe classify      - Classify a command >> release\README.txt
echo   openhuman-agent.exe execute       - Execute with security >> release\README.txt

echo.
echo Build complete! Output in: release\openhuman-agent\
dir release\openhuman-agent