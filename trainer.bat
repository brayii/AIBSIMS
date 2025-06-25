@echo off
setlocal enabledelayedexpansion

:: Set the number of runs
set RUNS=500

:: Loop counter
set COUNT=1

:loop
echo Running Bunny Simulation... (Run !COUNT! of %RUNS%)
python main.py

:: Wait a bit (optional)
sleep 1

:: Increment counter
set /a COUNT+=1

:: Check if done
if !COUNT! LEQ %RUNS% goto loop

echo Done running %RUNS% simulations.
pause
