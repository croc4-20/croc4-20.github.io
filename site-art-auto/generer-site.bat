@echo off
cd /d "%~dp0"
python generate.py
echo.
echo Appuyez sur une touche pour fermer.
pause >nul
