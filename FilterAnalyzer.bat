@echo off
REM 1. Activate the virtual environment
REM Replace 'venv' with your actual environment folder name
CALL .venv\Scripts\activate.bat

REM 2. Run your Python program
python FilterAnalyzer.py

REM 3. Deactivate the environment
CALL deactivate

pause