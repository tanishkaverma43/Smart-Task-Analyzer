@echo off
cd /d "%~dp0"
echo Starting Django server from backend directory...
echo.
python manage.py runserver 8000
pause

