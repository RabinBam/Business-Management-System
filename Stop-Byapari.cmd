@echo off
cd /d "%~dp0"
docker compose -f docker-compose.yml stop
echo Your workflows remain saved in Docker storage.
pause
