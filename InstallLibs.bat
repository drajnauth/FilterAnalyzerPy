@echo off
REM 1. Create virtual environment
python -m venv .venv

REM Activate the virtual environment
CALL .venv\Scripts\activate.bat

REM Install dependicies
pip install numpy matplotlib pillow

REM Deactivate the environment
CALL deactivate

pause