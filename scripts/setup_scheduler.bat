@echo off
:: Check for administrative privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges. Please run as administrator.
    pause
    exit /b
)

:: Set variables
SET TASK_NAME=SendEmailsTask
SET SCRIPT_PATH=D:\Portfolio\Automated Invoice and Report Generation System\main.py 
SET TIME=23:30

:: Create a scheduled task to run the Python script daily at the specified time
schtasks /create /tn %TASK_NAME% /tr "cmd.exe /c python %SCRIPT_PATH%" /sc daily /st %TIME% /rl HIGHEST /f

IF %ERRORLEVEL% EQU 0 (
    echo Scheduled task '%TASK_NAME%' created successfully to run daily at %TIME%.
) ELSE (
    echo Failed to create scheduled task.
)
pause
