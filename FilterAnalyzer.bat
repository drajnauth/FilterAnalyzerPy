@echo off
REM Activate the virtual environment
REM CALL is used in a batch file
CALL .venv\Scripts\activate.bat

REM Run your Python program
python FilterAnalyzer.py

REM Deactivate the environment
REM CALL is used in a batch file
CALL deactivate

pause