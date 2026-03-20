#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_federation.py

Generate RabbitMQ Federation configuration scripts from JSON config.
This script reads network_config.json and generates:
1. federation_setup.bat (Windows)
2. federation_setup.sh (Linux)
3. verify_federation.bat (verification script)

Usage:
    python scripts/generate_federation.py

Output:
    output/<node_name>/federation_setup.bat
    output/<node_name>/federation_setup.sh
    output/<node_name>/verify_federation.bat
"""

import json
import os
import sys
from datetime import datetime

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_config(config_path):
    """Load JSON configuration file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}❌ Error: Config file not found: {config_path}{Colors.ENDC}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}❌ Error: Invalid JSON in config file: {e}{Colors.ENDC}")
        sys.exit(1)

def generate_federation_batch(config, node):
    """Generate Windows batch script for RabbitMQ federation setup"""
    
    script = f"""@echo off
REM ============================================================================
REM  RabbitMQ Federation Setup Script
REM ============================================================================
REM  Node: {node['name']}
REM  IP: {node['ip']}
REM  Hostname: {node['hostname']}
REM  Location: {node['location']}
REM  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
REM ============================================================================
REM
REM  Instructions:
REM  1. Run this script as Administrator
REM  2. Wait for RabbitMQ to be installed and running
REM  3. Verify with: rabbitmqctl list_parameters
REM
REM ============================================================================

echo {Colors.OKCYAN}============================================================================{Colors.ENDC}
echo  RabbitMQ Federation Setup - {node['name']} ({node['ip']})
echo {Colors.OKCYAN}============================================================================{Colors.ENDC}
echo.

REM Check if RabbitMQ is installed
where rabbitmqctl >nul 2>&1
if %errorlevel% neq 0 (
    echo {Colors.FAIL}[ERROR] rabbitmqctl not found!{Colors.ENDC}
    echo Please install RabbitMQ first: https://rabbitmq.com/install-windows.html
    pause
    exit /b 1
)

echo {Colors.OKGREEN}[OK]{Colors.ENDC} RabbitMQ found
echo.

REM Step 1: Enable federation plugin
echo {Colors.OKBLUE}[STEP 1/3]{Colors.ENDC} Enabling federation plugin...
rabbitmq-plugins enable rabbitmq_federation
if %errorlevel% neq 0 (
    echo {Colors.FAIL}[ERROR] Failed to enable federation plugin{Colors.ENDC}
    pause
    exit /b 1
)
echo {Colors.OKGREEN}[OK]{Colors.ENDC} Federation plugin enabled
echo.

REM Step 2: Setup upstreams
echo {Colors.OKBLUE}[STEP 2/3]{Colors.ENDC} Setting up federation upstreams...
echo.

"""
    
    # Add upstream commands for all other nodes
    upstream_count = 0
    for other_node in config['nodes']:
        if other_node['name'] == node['name']:
            continue  # Skip self
        
        if not other_node.get('enabled', True):
            continue  # Skip disabled nodes
        
        upstream_count += 1
        
        script += f"""REM Upstream: {other_node['name']} ({other_node['ip']}) - {other_node['location']}
echo   Adding upstream: {other_node['name']} -&gt; {other_node['ip']}
rabbitmqctl set_parameter federation-upstream {other_node['name']} ^
  "{{\\"uri\\":\\"amqp://{config['rabbitmq_user']}:{config['rabbitmq_pass']}@{other_node['ip']}:{config['rabbitmq_port']}/\\", ^
   \\"exchange\\":\\"{config['exchange_name']}\\", ^
   \\"ack-mode\\":\\"{config['federation']['ack_mode']}\\", ^
   \\"max-hops\\":{config['federation']['max_hops']}, ^
   \\"prefetch-count\\":{config['federation']['prefetch_count']}}}"
if %errorlevel% neq 0 (
    echo {Colors.WARNING}[WARN]{Colors.ENDC} Failed to add upstream {other_node['name']}
) else (
    echo {Colors.OKGREEN}   [OK]{Colors.ENDC} Upstream {other_node['name']} added
)
echo.

"""
    
    script += f"""echo {Colors.OKGREEN}[OK]{Colors.ENDC} {upstream_count} upstream(s) configured
echo.

REM Step 3: Setup federation exchange
echo {Colors.OKBLUE}[STEP 3/3]{Colors.ENDC} Setting up federation exchange...
rabbitmqctl set_parameter federation-exchange {config['exchange_name']} ^
  "{{\\"upstream-set\\":\\"all\\"}}"
if %errorlevel% neq 0 (
    echo {Colors.FAIL}[ERROR] Failed to setup federation exchange{Colors.ENDC}
    pause
    exit /b 1
)
echo {Colors.OKGREEN}[OK]{Colors.ENDC} Federation exchange configured
echo.

REM Verification
echo {Colors.OKCYAN}============================================================================{Colors.ENDC}
echo  Setup Complete!
echo {Colors.OKCYAN}============================================================================{Colors.ENDC}
echo.
echo Node Information:
echo   - Name: {node['name']}
echo   - IP: {node['ip']}
echo   - Hostname: {node['hostname']}
echo   - Location: {node['location']}
echo.
echo Federation Summary:
echo   - Exchange: {config['exchange_name']}
echo   - Upstreams configured: {upstream_count}
echo   - Cluster: {config['cluster_name']}
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

echo {Colors.OKGREEN}✓ Federation setup complete for {node['name']}!{Colors.ENDC}
echo.
pause
"""
    
    return script

def generate_federation_shell(config, node):
    """Generate Linux shell script for RabbitMQ federation setup"""
    
    script = f"""#!/bin/bash
# ============================================================================
#  RabbitMQ Federation Setup Script (Linux)
# ============================================================================
#  Node: {node['name']}
#  IP: {node['ip']}
#  Hostname: {node['hostname']}
#  Location: {node['location']}
#  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================================================

set -e  # Exit on error

GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
CYAN='\\033[0;36m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

echo -e "${{CYAN}}============================================================================${{NC}}"
echo -e " RabbitMQ Federation Setup - {node['name']} ({node['ip']})"
echo -e "${{CYAN}}============================================================================${{NC}}"
echo ""

# Check if RabbitMQ is installed
if ! command -v rabbitmqctl &> /dev/null; then
    echo -e "${{RED}}[ERROR] rabbitmqctl not found!${{NC}}"
    echo "Please install RabbitMQ first: https://rabbitmq.com/download.html"
    exit 1
fi

echo -e "${{GREEN}}[OK]${{NC}} RabbitMQ found"
echo ""

# Step 1: Enable federation plugin
echo -e "${{BLUE}}[STEP 1/3]${{NC}} Enabling federation plugin..."
rabbitmq-plugins enable rabbitmq_federation
echo -e "${{GREEN}}[OK]${{NC}} Federation plugin enabled"
echo ""

# Step 2: Setup upstreams
echo -e "${{BLUE}}[STEP 2/3]${{NC}} Setting up federation upstreams..."
echo ""

"""
    
    # Add upstream commands for all other nodes
    for other_node in config['nodes']:
        if other_node['name'] == node['name']:
            continue
        
        if not other_node.get('enabled', True):
            continue
        
        script += f"""# Upstream: {other_node['name']} ({other_node['ip']})
echo -e "  Adding upstream: {other_node['name']} -> {other_node['ip']}"
rabbitmqctl set_parameter federation-upstream {other_node['name']} \\
  '{{"uri":"amqp://{config['rabbitmq_user']}:{config['rabbitmq_pass']}@{other_node['ip']}:{config['rabbitmq_port']}/", \\
   "exchange":"{config['exchange_name']}", \\
   "ack-mode":"{config['federation']['ack_mode']}", \\
   "max-hops":{config['federation']['max_hops']}, \\
   "prefetch-count":{config['federation']['prefetch_count']}}}'
echo -e "${{GREEN}}  [OK]${{NC}} Upstream {other_node['name']} added"
echo ""

"""
    
    script += f"""# Step 3: Setup federation exchange
echo -e "${{BLUE}}[STEP 3/3]${{NC}} Setting up federation exchange..."
rabbitmqctl set_parameter federation-exchange {config['exchange_name']} \\
  '{{"upstream-set":"all"}}'
echo -e "${{GREEN}}[OK]${{NC}} Federation exchange configured"
echo ""

# Verification
echo -e "${{CYAN}}============================================================================${{NC}}"
echo -e " Setup Complete!"
echo -e "${{CYAN}}============================================================================${{NC}}"
echo ""
echo "Node Information:"
echo "  - Name: {node['name']}"
echo "  - IP: {node['ip']}"
echo "  - Hostname: {node['hostname']}"
echo "  - Location: {node['location']}"
echo ""
echo "Federation Summary:"
echo "  - Exchange: {config['exchange_name']}"
echo "  - Upstreams configured: {sum(1 for n in config['nodes'] if n['name'] != node['name'] and n.get('enabled', True))}"
echo "  - Cluster: {config['cluster_name']}"
echo ""
echo "Next Steps:"
echo "  1. Start RabbitMQ: sudo systemctl start rabbitmq-server"
echo "  2. Run docker-compose up -d"
echo "  3. Verify: rabbitmqctl list_parameters"
echo ""

# List configured parameters
echo "Configured Parameters:"
echo "----------------------"
rabbitmqctl list_parameters
echo ""

echo -e "${{GREEN}}✓ Federation setup complete for {node['name']}!${{NC}}"
"""
    
    return script

def generate_verify_script(config, node):
    """Generate verification script"""
    
    script = f"""@echo off
REM ============================================================================
REM  RabbitMQ Federation Verification Script
REM ============================================================================
REM  Node: {node['name']}
REM  IP: {node['ip']}
REM ============================================================================

echo ============================================================================
echo  RabbitMQ Federation Verification - {node['name']}
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

"""
    
    for other_node in config['nodes']:
        if other_node['name'] == node['name']:
            continue
        
        if not other_node.get('enabled', True):
            continue
        
        script += f"""echo   Testing connection to {other_node['name']} ({other_node['ip']})...
powershell -Command "Test-NetConnection -ComputerName {other_node['ip']} -Port {config['rabbitmq_port']} -InformationLevel Quiet" >nul 2>&1
if %errorlevel% equ 0 (
    echo   {Colors.OKGREEN}[OK]{Colors.ENDC} {other_node['name']} is reachable
) else (
    echo   {Colors.FAIL}[FAIL]{Colors.ENDC} {other_node['name']} is NOT reachable
)
echo.

"""
    
    script += """echo ============================================================================
echo  Verification Complete!
echo ============================================================================
echo.
pause
"""
    
    return script

def main():
    """Main function"""
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}  RabbitMQ Federation Config Generator{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print()
    
    # Determine config path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, 'config', 'network_config.json')
    output_dir = os.path.join(project_root, 'output')
    
    print(f"{Colors.OKBLUE}Config file:{Colors.ENDC} {config_path}")
    print(f"{Colors.OKBLUE}Output directory:{Colors.ENDC} {output_dir}")
    print()
    
    # Load configuration
    print(f"{Colors.OKCYAN}Loading configuration...{Colors.ENDC}")
    config = load_config(config_path)
    print(f"{Colors.OKGREEN}✓ Loaded {len(config['nodes'])} nodes from config{Colors.ENDC}")
    print()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate config for each node
    enabled_nodes = [n for n in config['nodes'] if n.get('enabled', True)]
    
    for node in enabled_nodes:
        print(f"{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}Generating config for: {Colors.OKCYAN}{node['name']}{Colors.ENDC} {Colors.BOLD}({node['ip']}){Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
        
        # Create node output directory
        node_output_dir = os.path.join(output_dir, node['name'])
        os.makedirs(node_output_dir, exist_ok=True)
        
        # Generate Windows batch script
        batch_script = generate_federation_batch(config, node)
        batch_file = os.path.join(node_output_dir, 'federation_setup.bat')
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_script)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: federation_setup.bat")
        
        # Generate Linux shell script
        shell_script = generate_federation_shell(config, node)
        shell_file = os.path.join(node_output_dir, 'federation_setup.sh')
        with open(shell_file, 'w', encoding='utf-8') as f:
            f.write(shell_script)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: federation_setup.sh")
        
        # Generate verification script
        verify_script = generate_verify_script(config, node)
        verify_file = os.path.join(node_output_dir, 'verify_federation.bat')
        with open(verify_file, 'w', encoding='utf-8') as f:
            f.write(verify_script)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: verify_federation.bat")
        
        # Generate config summary
        summary_file = os.path.join(node_output_dir, 'config_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"RabbitMQ Federation Configuration Summary\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Node Name: {node['name']}\n")
            f.write(f"Node IP: {node['ip']}\n")
            f.write(f"Hostname: {node['hostname']}\n")
            f.write(f"Location: {node['location']}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Federation Configuration:\n")
            f.write(f"  Cluster: {config['cluster_name']}\n")
            f.write(f"  Exchange: {config['exchange_name']}\n")
            f.write(f"  Upstreams: {sum(1 for n in config['nodes'] if n['name'] != node['name'] and n.get('enabled', True))}\n\n")
            f.write(f"Upstream Nodes:\n")
            for other_node in config['nodes']:
                if other_node['name'] != node['name'] and other_node.get('enabled', True):
                    f.write(f"  - {other_node['name']}: {other_node['ip']} ({other_node['location']})\n")
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: config_summary.txt")
        
        print()
    
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Generation Complete!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print()
    print(f"Output directory: {output_dir}")
    print()
    print("Next steps:")
    print(f"  1. Copy output/{Colors.OKCYAN}<node_name>{Colors.ENDC} folder to respective PC")
    print(f"  2. Run {Colors.OKCYAN}federation_setup.bat{Colors.ENDC} as Administrator on each PC")
    print(f"  3. Run {Colors.OKCYAN}docker-compose up -d{Colors.ENDC} on each PC")
    print(f"  4. Verify with {Colors.OKCYAN}verify_federation.bat{Colors.ENDC}")
    print()

if __name__ == "__main__":
    main()
