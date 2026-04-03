@echo off
set "PYTHON_EXE=C:\HDT\Nikolai\venv\Scripts\python.exe"
title EgoWeaver 2.0 Engine
echo [SYSTEM] Initiating Weaving Process...
:: Ensure we are in the script directory
cd /d "%~dp0"
"%PYTHON_EXE%" egoweaver.py
echo.
echo [SYSTEM] Process Complete. Check the 'output' folder for your context records.
pause