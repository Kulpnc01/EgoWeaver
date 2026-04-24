@echo off
set "PYTHON_EXE=C:\HDT\Nikolai\venv\Scripts\python.exe"
title EgoWeaver Pipeline
echo Initiating EgoWeaver...
cd /d "C:\HDT\EgoWeaver"
"%PYTHON_EXE%" egoweaver.py
echo.
pause