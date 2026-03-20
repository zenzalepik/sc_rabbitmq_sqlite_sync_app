@echo off
echo ========================================
echo  Starting RabbitMQ + Chat Apps (Docker)
echo ========================================
echo.
echo NOTE: This is for SINGLE-PC testing (App A + App B)
echo For multi-PC federation, use output/<node_name>/start.bat
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

REM Build and start containers
echo Building images...
docker-compose build

echo.
echo Starting containers...
docker-compose up -d

echo.
echo ========================================
echo  Containers Started!
echo ========================================
echo.
echo Services:
echo   - RabbitMQ Broker
echo   - Chat App A
echo   - Chat App B
echo.
echo RabbitMQ Management UI: http://localhost:15672
echo   Username: guest
echo   Password: guest
echo.
echo To view logs:
echo   docker-compose logs -f app_a
echo   docker-compose logs -f app_b
echo   docker-compose logs -f rabbitmq
echo.
echo To stop:
echo   stop.bat
echo ========================================

REM Show running containers
docker-compose ps
