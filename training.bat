@echo off
:loop
echo Running Bunny Simulation...
python main.py
timeout /t 2 >nul
goto loop

