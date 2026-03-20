@echo off
REM ============================================================================
REM  RabbitMQ Federation Setup Script
REM ============================================================================
REM  Node: pc9
REM  IP: 192.168.1.18
REM  Hostname: pc9.local
REM  Location: Office - Room 9
REM  Generated: 2026-03-20 11:09:16
REM ============================================================================
REM
REM  Instructions:
REM  1. Run this script as Administrator
REM  2. Wait for RabbitMQ to be installed and running
REM  3. Verify with: rabbitmqctl list_parameters
REM
REM ============================================================================

echo ============================================================================
echo  RabbitMQ Federation Setup - pc9 (192.168.1.18)
echo ============================================================================
echo.

REM Check if RabbitMQ is installed
where rabbitmqctl >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] rabbitmqctl not found!
    echo Please install RabbitMQ first: https://rabbitmq.com/install-windows.html
    pause
    exit /b 1
)

echo [OK] RabbitMQ found
echo.

REM Step 1: Enable federation plugin
echo [STEP 1/3] Enabling federation plugin...
rabbitmq-plugins enable rabbitmq_federation
if %errorlevel% neq 0 (
    echo [ERROR] Failed to enable federation plugin
    pause
    exit /b 1
)
echo [OK] Federation plugin enabled
echo.

REM Step 2: Setup upstreams
echo [STEP 2/3] Setting up federation upstreams...
echo.

REM Upstream: pc1 (192.168.1.10) - Office - Room 1
echo   Adding upstream: pc1 -^> 192.168.1.10
rabbitmqctl set_parameter federation-upstream pc1 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.10:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc1
) else (
    echo   [OK] Upstream pc1 added
)
echo.

REM Upstream: pc2 (192.168.1.11) - Office - Room 2
echo   Adding upstream: pc2 -^> 192.168.1.11
rabbitmqctl set_parameter federation-upstream pc2 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.11:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc2
) else (
    echo   [OK] Upstream pc2 added
)
echo.

REM Upstream: pc3 (192.168.1.12) - Office - Room 3
echo   Adding upstream: pc3 -^> 192.168.1.12
rabbitmqctl set_parameter federation-upstream pc3 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.12:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc3
) else (
    echo   [OK] Upstream pc3 added
)
echo.

REM Upstream: pc4 (192.168.1.13) - Office - Room 4
echo   Adding upstream: pc4 -^> 192.168.1.13
rabbitmqctl set_parameter federation-upstream pc4 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.13:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc4
) else (
    echo   [OK] Upstream pc4 added
)
echo.

REM Upstream: pc5 (192.168.1.14) - Office - Room 5
echo   Adding upstream: pc5 -^> 192.168.1.14
rabbitmqctl set_parameter federation-upstream pc5 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.14:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc5
) else (
    echo   [OK] Upstream pc5 added
)
echo.

REM Upstream: pc6 (192.168.1.15) - Office - Room 6
echo   Adding upstream: pc6 -^> 192.168.1.15
rabbitmqctl set_parameter federation-upstream pc6 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.15:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc6
) else (
    echo   [OK] Upstream pc6 added
)
echo.

REM Upstream: pc7 (192.168.1.16) - Office - Room 7
echo   Adding upstream: pc7 -^> 192.168.1.16
rabbitmqctl set_parameter federation-upstream pc7 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.16:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc7
) else (
    echo   [OK] Upstream pc7 added
)
echo.

REM Upstream: pc8 (192.168.1.17) - Office - Room 8
echo   Adding upstream: pc8 -^> 192.168.1.17
rabbitmqctl set_parameter federation-upstream pc8 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.17:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc8
) else (
    echo   [OK] Upstream pc8 added
)
echo.

REM Upstream: pc10 (192.168.1.19) - Office - Room 10
echo   Adding upstream: pc10 -^> 192.168.1.19
rabbitmqctl set_parameter federation-upstream pc10 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.19:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [WARN] Failed to add upstream pc10
) else (
    echo   [OK] Upstream pc10 added
)
echo.

echo [OK] 9 upstream(s) configured
echo.

REM Step 3: Setup federation exchange
echo [STEP 3/3] Setting up federation exchange...
rabbitmqctl set_parameter federation-exchange chat_exchange ^
  "{\"upstream-set\":\"all\"}"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to setup federation exchange
    pause
    exit /b 1
)
echo [OK] Federation exchange configured
echo.

REM Verification
echo ============================================================================
echo  Setup Complete!
echo ============================================================================
echo.
echo Node Information:
echo   - Name: pc9
echo   - IP: 192.168.1.18
echo   - Hostname: pc9.local
echo   - Location: Office - Room 9
echo.
echo Federation Summary:
echo   - Exchange: chat_exchange
echo   - Upstreams configured: 9
echo   - Cluster: chat_federation
echo.
echo Next Steps:
echo   1. Start RabbitMQ service (if not running)
echo   2. Run docker-compose up -d
echo   3. Verify federation: rabbitmqctl list_parameters
echo.

REM List configured parameters
echo Configured Parameters:
echo ----------------------
rabbitmqctl list_parameters
echo.

echo Federation setup complete for pc9!
echo.
pause
