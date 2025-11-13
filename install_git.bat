@echo off
REM Install Git for Windows using winget (Windows Package Manager)
REM Make sure you have Windows 10/11 with winget installed

echo Installing Git for Windows...
winget install --id Git.Git -e --source winget

if %ERRORLEVEL% EQU 0 (
    echo Git installed successfully!
    echo Restart PowerShell and run:
    echo cd C:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final
    echo .\push_to_github.ps1 -RepoUrl 'https://github.com/cyberworld360/cyberworld-store.git'
) else (
    echo Git installation failed or not available via winget.
    echo Please install Git manually from: https://git-scm.com/download/win
    pause
)
