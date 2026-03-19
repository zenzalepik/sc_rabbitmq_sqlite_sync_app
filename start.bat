@echo off
echo ========================================
echo  Starting RabbitMQ + Chat Apps (Docker)
echo ========================================
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
echo Container IPs:
echo   - RabbitMQ: 172.28.0.2
echo   - App A:    172.28.0.3
echo   - App B:    172.28.0.4
echo.
echo RabbitMQ Management UI: http://localhost:15672
echo   Username: guest
echo   Password: guest
echo.
echo To view logs:
echo   docker-compose logs -f app_a
echo   docker-compose logs -f app_b
echo.
echo To stop:
echo   docker-compose down
echo ========================================

REM Show running containers
docker-compose ps
