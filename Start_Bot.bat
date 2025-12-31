@echo off
title Instagram Bot - Local Worker 👷‍♂️
color 0A

echo ========================================================
echo   INSTAGRAM BOT - LOCAL WORKER (REMOTE CONTROL MODE)
echo ========================================================
echo.
echo [1] Checking Environment...
cd /d "%~dp0"

if not exist dev.vars (
    echo [WARNING] dev.vars not found! Please ensure it exists.
)

echo [2] Connecting to Cloud Control (Supabase)...
echo.
echo 👷 Worker is STARTING...
echo 📱 You can now go to the Website on your Phone and add links.
echo 💻 This window will execute them automatically using YOUR Internet.
echo.
echo [PRESS CTRL+C TO STOP]
echo.

python local_worker.py

pause
