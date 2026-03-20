@echo off
REM ============================================================================
REM  Start Chat App (Docker)
REM ============================================================================
REM  Node: pc3
REM  IP: 192.168.1.12
REM  Location: Office - Room 3
REM ============================================================================

echo ============================================================================
echo  Starting Chat App - pc3 (192.168.1.12)
echo ============================================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Load environment variables
if exist .env (
    echo [INFO] Loading .env file...
)

REM Build and start containers
echo Building images...
docker-compose build

echo.
echo Starting containers...
docker-compose up -d

echo.
echo Waiting for RabbitMQ to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo ============================================================================
echo  Status
echo ============================================================================
docker-compose ps

echo.
echo RabbitMQ Management UI: http://192.168.1.12:15672
echo Username: guest
echo Password: guest
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop:
echo   stop.bat
echo ============================================================================
echo.
