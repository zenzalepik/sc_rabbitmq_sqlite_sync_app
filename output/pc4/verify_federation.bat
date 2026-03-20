@echo off
REM ============================================================================
REM  RabbitMQ Federation Verification Script
REM ============================================================================
REM  Node: pc4
REM  IP: 192.168.1.13
REM ============================================================================

echo ============================================================================
echo  RabbitMQ Federation Verification - pc4
echo ============================================================================
echo.

REM Check RabbitMQ status
echo [1] Checking RabbitMQ status...
rabbitmqctl status
echo.

REM List parameters
echo [2] Listing federation parameters...
rabbitmqctl list_parameters
echo.

REM List upstreams
echo [3] Listing federation upstreams...
rabbitmqctl list_parameters federation-upstream
echo.

REM List exchanges
echo [4] Listing exchanges...
rabbitmqctl list_exchanges
echo.

REM Test connection to all upstreams
echo [5] Testing connections to upstream nodes...
echo.

echo   Testing connection to pc1 (192.168.1.10)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.10 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc1 is reachable
) else (
    echo   [91m[FAIL][0m pc1 is NOT reachable
)
echo.

echo   Testing connection to pc2 (192.168.1.11)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.11 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc2 is reachable
) else (
    echo   [91m[FAIL][0m pc2 is NOT reachable
)
echo.

echo   Testing connection to pc3 (192.168.1.12)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.12 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc3 is reachable
) else (
    echo   [91m[FAIL][0m pc3 is NOT reachable
)
echo.

echo   Testing connection to pc5 (192.168.1.14)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.14 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc5 is reachable
) else (
    echo   [91m[FAIL][0m pc5 is NOT reachable
)
echo.

echo   Testing connection to pc6 (192.168.1.15)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.15 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc6 is reachable
) else (
    echo   [91m[FAIL][0m pc6 is NOT reachable
)
echo.

echo   Testing connection to pc7 (192.168.1.16)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.16 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc7 is reachable
) else (
    echo   [91m[FAIL][0m pc7 is NOT reachable
)
echo.

echo   Testing connection to pc8 (192.168.1.17)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.17 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc8 is reachable
) else (
    echo   [91m[FAIL][0m pc8 is NOT reachable
)
echo.

echo   Testing connection to pc9 (192.168.1.18)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.18 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc9 is reachable
) else (
    echo   [91m[FAIL][0m pc9 is NOT reachable
)
echo.

echo   Testing connection to pc10 (192.168.1.19)...
powershell -Command "Test-NetConnection -ComputerName 192.168.1.19 -Port 5672 -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [92m[OK][0m pc10 is reachable
) else (
    echo   [91m[FAIL][0m pc10 is NOT reachable
)
echo.

echo ============================================================================
echo  Verification Complete!
echo ============================================================================
echo.
pause
