@echo off
set "PYTHON_EXE=C:\HDT\Nikolai\venv\Scripts\python.exe"
title Set EgoWeaver Output
echo Setting current directory as EgoWeaver Output Destination...
"%PYTHON_EXE%" "C:\HDT\EgoWeaver\egoweaver.py" --set-output "%CD%"
pause