@echo off
echo ========================================
echo  View Logs - Chat Apps
echo ========================================
echo.
echo Select container to view:
echo   1. App A
echo   2. App B
echo   3. RabbitMQ
echo   4. All (follow mode)
echo   5. Exit
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" docker-compose logs -f app_a
if "%choice%"=="2" docker-compose logs -f app_b
if "%choice%"=="3" docker-compose logs -f rabbitmq
if "%choice%"=="4" docker-compose logs -f
if "%choice%"=="5" exit /b
