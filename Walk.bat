@echo off
REM Change the directory
cd /d D:\NOVA\nova-tehnical

REM Run the poetry command
poetry run -C nova-py nova process --scenario walk --debug

REM If you want the command prompt window to remain open after the script finishes, uncomment the next line.
REM pause