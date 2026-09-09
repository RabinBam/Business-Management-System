@echo off
cd /d "%~dp0"
where docker >nul 2>&1
if errorlevel 1 (
  echo Install Docker Desktop first. See docs\INSTALL_WINDOWS.md.
  pause
  exit /b 1
)
if not exist .env (
  copy .env.example .env >nul
  echo Created .env. The app starts in free mock mode.
  echo To use OpenRouter, edit .env using docs\INSTALL_WINDOWS.md.
)
docker info >nul 2>&1
if errorlevel 1 (
  echo Start Docker Desktop and wait until its engine is running, then try again.
  pause
  exit /b 1
)
docker compose -f docker-compose.yml up -d --build --force-recreate --wait --wait-timeout 180
if errorlevel 1 (
  echo Startup failed. See the error above and docs\INSTALL_WINDOWS.md.
  pause
  exit /b 1
)
echo AegisFlow is running. Default address: http://localhost:3000
echo If you customized FRONTEND_PORT, use that port instead.
pause
