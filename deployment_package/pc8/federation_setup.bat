@echo off
REM ============================================================================
REM  RabbitMQ Federation Setup Script
REM ============================================================================
REM  Node: pc8
REM  IP: 192.168.1.17
REM  Hostname: pc8.local
REM  Location: Office - Room 8
REM  Generated: 2026-03-20 09:39:20
REM ============================================================================
REM
REM  Instructions:
REM  1. Run this script as Administrator
REM  2. Wait for RabbitMQ to be installed and running
REM  3. Verify with: rabbitmqctl list_parameters
REM
REM ============================================================================

echo [96m============================================================================[0m
echo  RabbitMQ Federation Setup - pc8 (192.168.1.17)
echo [96m============================================================================[0m
echo.

REM Check if RabbitMQ is installed
where rabbitmqctl >nul 2>&1
if %errorlevel% neq 0 (
    echo [91m[ERROR] rabbitmqctl not found![0m
    echo Please install RabbitMQ first: https://rabbitmq.com/install-windows.html
    pause
    exit /b 1
)

echo [92m[OK][0m RabbitMQ found
echo.

REM Step 1: Enable federation plugin
echo [94m[STEP 1/3][0m Enabling federation plugin...
rabbitmq-plugins enable rabbitmq_federation
if %errorlevel% neq 0 (
    echo [91m[ERROR] Failed to enable federation plugin[0m
    pause
    exit /b 1
)
echo [92m[OK][0m Federation plugin enabled
echo.

REM Step 2: Setup upstreams
echo [94m[STEP 2/3][0m Setting up federation upstreams...
echo.

REM Upstream: pc1 (192.168.1.10) - Office - Room 1
echo   Adding upstream: pc1 -&gt; 192.168.1.10
rabbitmqctl set_parameter federation-upstream pc1 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.10:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc1
) else (
    echo [92m   [OK][0m Upstream pc1 added
)
echo.

REM Upstream: pc2 (192.168.1.11) - Office - Room 2
echo   Adding upstream: pc2 -&gt; 192.168.1.11
rabbitmqctl set_parameter federation-upstream pc2 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.11:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc2
) else (
    echo [92m   [OK][0m Upstream pc2 added
)
echo.

REM Upstream: pc3 (192.168.1.12) - Office - Room 3
echo   Adding upstream: pc3 -&gt; 192.168.1.12
rabbitmqctl set_parameter federation-upstream pc3 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.12:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc3
) else (
    echo [92m   [OK][0m Upstream pc3 added
)
echo.

REM Upstream: pc4 (192.168.1.13) - Office - Room 4
echo   Adding upstream: pc4 -&gt; 192.168.1.13
rabbitmqctl set_parameter federation-upstream pc4 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.13:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc4
) else (
    echo [92m   [OK][0m Upstream pc4 added
)
echo.

REM Upstream: pc5 (192.168.1.14) - Office - Room 5
echo   Adding upstream: pc5 -&gt; 192.168.1.14
rabbitmqctl set_parameter federation-upstream pc5 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.14:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc5
) else (
    echo [92m   [OK][0m Upstream pc5 added
)
echo.

REM Upstream: pc6 (192.168.1.15) - Office - Room 6
echo   Adding upstream: pc6 -&gt; 192.168.1.15
rabbitmqctl set_parameter federation-upstream pc6 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.15:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc6
) else (
    echo [92m   [OK][0m Upstream pc6 added
)
echo.

REM Upstream: pc7 (192.168.1.16) - Office - Room 7
echo   Adding upstream: pc7 -&gt; 192.168.1.16
rabbitmqctl set_parameter federation-upstream pc7 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.16:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc7
) else (
    echo [92m   [OK][0m Upstream pc7 added
)
echo.

REM Upstream: pc9 (192.168.1.18) - Office - Room 9
echo   Adding upstream: pc9 -&gt; 192.168.1.18
rabbitmqctl set_parameter federation-upstream pc9 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.18:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc9
) else (
    echo [92m   [OK][0m Upstream pc9 added
)
echo.

REM Upstream: pc10 (192.168.1.19) - Office - Room 10
echo   Adding upstream: pc10 -&gt; 192.168.1.19
rabbitmqctl set_parameter federation-upstream pc10 ^
  "{\"uri\":\"amqp://guest:guest@192.168.1.19:5672/\", ^
   \"exchange\":\"chat_exchange\", ^
   \"ack-mode\":\"on-confirm\", ^
   \"max-hops\":1, ^
   \"prefetch-count\":100}"
if %errorlevel% neq 0 (
    echo [93m[WARN][0m Failed to add upstream pc10
) else (
    echo [92m   [OK][0m Upstream pc10 added
)
echo.

echo [92m[OK][0m 9 upstream(s) configured
echo.

REM Step 3: Setup federation exchange
echo [94m[STEP 3/3][0m Setting up federation exchange...
rabbitmqctl set_parameter federation-exchange chat_exchange ^
  "{\"upstream-set\":\"all\"}"
if %errorlevel% neq 0 (
    echo [91m[ERROR] Failed to setup federation exchange[0m
    pause
    exit /b 1
)
echo [92m[OK][0m Federation exchange configured
echo.

REM Verification
echo [96m============================================================================[0m
echo  Setup Complete!
echo [96m============================================================================[0m
echo.
echo Node Information:
echo   - Name: pc8
echo   - IP: 192.168.1.17
echo   - Hostname: pc8.local
echo   - Location: Office - Room 8
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

echo [92m✓ Federation setup complete for pc8![0m
echo.
pause
