#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_docker_compose.py

Generate Docker Compose files and environment files for each node from JSON config.

Usage:
    python scripts/generate_docker_compose.py

Output:
    output/<node_name>/docker-compose.yml
    output/<node_name>/.env
    output/<node_name>/start.bat
    output/<node_name>/stop.bat
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

def generate_docker_compose(config, node):
    """Generate docker-compose.yml for a single node"""
    
    # Calculate subnet from IP (e.g., 192.168.1.10 → 192.168.1)
    ip_parts = node['ip'].split('.')
    subnet_base = '.'.join(ip_parts[:3])
    
    compose = f"""# ============================================================================
#  Docker Compose for RabbitMQ Federation Chat App
# ============================================================================
#  Node: {node['name']}
#  IP: {node['ip']}
#  Hostname: {node['hostname']}
#  Location: {node['location']}
#  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================================================

services:
  # ============================================================================
  #  RabbitMQ Broker with Federation
  # ============================================================================
  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq_broker
    hostname: {node['name']}
    networks:
      - chat_network
    ports:
      - "{config['rabbitmq_port']}:5672"      # AMQP port
      - "{config['management_port']}:15672"   # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: {config['rabbitmq_user']}
      RABBITMQ_DEFAULT_PASS: {config['rabbitmq_pass']}
    volumes:
      - ./rabbitmq_data:/var/lib/rabbitmq
    command: >
      sh -c "rabbitmq-plugins enable rabbitmq_federation &&
             rabbitmq-server"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ============================================================================
  #  Chat Application
  # ============================================================================
  chat_app:
    build:
      context: ./app
      dockerfile: ../Dockerfile
    container_name: chat_app_{node['name']}
    hostname: app_{node['name']}
    networks:
      - chat_network
    volumes:
      - ./app:/app
      - ./chat.db:/app/chat.db
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - PYTHONUNBUFFERED=1
      - RABBITMQ_HOST={node['ip']}
      - RABBITMQ_PORT={config['rabbitmq_port']}
      - RABBITMQ_USER={config['rabbitmq_user']}
      - RABBITMQ_PASS={config['rabbitmq_pass']}
      - NODE_NAME={node['name']}
      - NODE_IP={node['ip']}
      - NODE_HOSTNAME={node['hostname']}
      - EXCHANGE_NAME={config['exchange_name']}
      - CLUSTER_NAME={config['cluster_name']}
    stdin_open: true
    tty: true
    command: >
      sh -c "pip install -r requirements.txt &&
             python sync_chatting_app.py"
    restart: unless-stopped

# ============================================================================
#  Network Configuration
# ============================================================================
networks:
  chat_network:
    driver: bridge
    ipam:
      config:
        - subnet: {subnet_base}.0/24
          gateway: {subnet_base}.1
"""
    
    return compose

def generate_env_file(config, node):
    """Generate .env file for a single node"""
    
    # Get all other node IPs for reference
    other_nodes = [n for n in config['nodes'] 
                   if n['name'] != node['name'] and n.get('enabled', True)]
    
    env_content = f"""# ============================================================================
#  Environment Configuration for Chat App
# ============================================================================
#  Node: {node['name']}
#  IP: {node['ip']}
#  Hostname: {node['hostname']}
#  Location: {node['location']}
#  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ============================================================================

# ----------------------------------------------------------------------------
# Node Identity
# ----------------------------------------------------------------------------
NODE_NAME={node['name']}
NODE_IP={node['ip']}
NODE_HOSTNAME={node['hostname']}
NODE_LOCATION={node['location']}
DEFAULT_USERNAME={node.get('username', 'user_' + node['name'])}

# ----------------------------------------------------------------------------
# RabbitMQ Connection (Local)
# ----------------------------------------------------------------------------
RABBITMQ_HOST={node['ip']}
RABBITMQ_PORT={config['rabbitmq_port']}
RABBITMQ_USER={config['rabbitmq_user']}
RABBITMQ_PASS={config['rabbitmq_pass']}

# ----------------------------------------------------------------------------
# Federation Configuration
# ----------------------------------------------------------------------------
EXCHANGE_NAME={config['exchange_name']}
CLUSTER_NAME={config['cluster_name']}
FEDERATION_ACK_MODE={config['federation']['ack_mode']}
FEDERATION_MAX_HOPS={config['federation']['max_hops']}
FEDERATION_PREFETCH_COUNT={config['federation']['prefetch_count']}

# ----------------------------------------------------------------------------
# Peer Nodes (Reference - for troubleshooting)
# ----------------------------------------------------------------------------
# Total peer nodes: {len(other_nodes)}
PEER_NODES={','.join([n['ip'] for n in other_nodes])}
PEER_NAMES={','.join([n['name'] for n in other_nodes])}

# ----------------------------------------------------------------------------
# Application Settings
# ----------------------------------------------------------------------------
PYTHONUNBUFFERED=1
TZ=Asia/Jakarta

# ----------------------------------------------------------------------------
# Docker Settings
# ----------------------------------------------------------------------------
COMPOSE_PROJECT_NAME={config['cluster_name']}_{node['name']}
"""
    
    return env_content

def generate_start_batch(config, node):
    """Generate start.bat for a single node"""
    
    batch = f"""@echo off
REM ============================================================================
REM  Start Chat App (Docker)
REM ============================================================================
REM  Node: {node['name']}
REM  IP: {node['ip']}
REM  Location: {node['location']}
REM ============================================================================

echo ============================================================================
echo  Starting Chat App - {node['name']} ({node['ip']})
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
echo RabbitMQ Management UI: http://{node['ip']}:{config['management_port']}
echo Username: {config['rabbitmq_user']}
echo Password: {config['rabbitmq_pass']}
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop:
echo   stop.bat
echo ============================================================================
echo.
"""
    
    return batch

def generate_stop_batch(config, node):
    """Generate stop.bat for a single node"""
    
    batch = f"""@echo off
REM ============================================================================
REM  Stop Chat App (Docker)
REM ============================================================================
REM  Node: {node['name']}
REM  IP: {node['ip']}
REM ============================================================================

echo ============================================================================
echo  Stopping Chat App - {node['name']}
echo ============================================================================
echo.

docker-compose down

echo.
echo All containers stopped.
echo.
pause
"""
    
    return batch

def generate_readme(config, node):
    """Generate README for a single node"""
    
    other_nodes = [n for n in config['nodes'] 
                   if n['name'] != node['name'] and n.get('enabled', True)]
    
    readme = f"""# Chat App - {node['name']}

## Node Information

| Property | Value |
|----------|-------|
| **Name** | {node['name']} |
| **IP Address** | {node['ip']} |
| **Hostname** | {node['hostname']} |
| **Location** | {node['location']} |
| **Default Username** | {node.get('username', 'user_' + node['name'])} |

## Quick Start

### 1. Setup RabbitMQ Federation

Run as Administrator:
```batch
federation_setup.bat
```

### 2. Start Docker Containers

```batch
start.bat
```

### 3. Access Chat App

```batch
docker exec -it chat_app_{node['name']} python sync_chatting_app.py
```

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| RabbitMQ AMQP | `{node['ip']}:{config['rabbitmq_port']}` | {config['rabbitmq_user']}/{config['rabbitmq_pass']} |
| RabbitMQ Management | http://{node['ip']}:{config['management_port']} | {config['rabbitmq_user']}/{config['rabbitmq_pass']} |

## Connected Peer Nodes ({len(other_nodes)} nodes)

"""
    
    for other_node in other_nodes:
        readme += f"- **{other_node['name']}**: {other_node['ip']} ({other_node['location']})\n"
    
    readme += f"""
## Troubleshooting

### Check RabbitMQ Status
```batch
rabbitmqctl status
```

### Verify Federation
```batch
verify_federation.bat
```

### View Docker Logs
```batch
docker-compose logs -f
```

### Restart Services
```batch
stop.bat
start.bat
```

## Files

- `docker-compose.yml` - Docker Compose configuration
- `.env` - Environment variables
- `federation_setup.bat` - RabbitMQ federation setup
- `verify_federation.bat` - Federation verification
- `start.bat` - Start all containers
- `stop.bat` - Stop all containers

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return readme

def main():
    """Main function"""
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}  Docker Compose Config Generator{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print()
    
    # Determine paths
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
        
        # Generate docker-compose.yml
        compose_content = generate_docker_compose(config, node)
        compose_file = os.path.join(node_output_dir, 'docker-compose.yml')
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: docker-compose.yml")
        
        # Generate .env
        env_content = generate_env_file(config, node)
        env_file = os.path.join(node_output_dir, '.env')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: .env")
        
        # Generate start.bat
        start_content = generate_start_batch(config, node)
        start_file = os.path.join(node_output_dir, 'start.bat')
        with open(start_file, 'w', encoding='utf-8') as f:
            f.write(start_content)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: start.bat")
        
        # Generate stop.bat
        stop_content = generate_stop_batch(config, node)
        stop_file = os.path.join(node_output_dir, 'stop.bat')
        with open(stop_file, 'w', encoding='utf-8') as f:
            f.write(stop_content)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: stop.bat")
        
        # Generate README.md
        readme_content = generate_readme(config, node)
        readme_file = os.path.join(node_output_dir, 'README.md')
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Generated: README.md")
        
        print()
    
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Generation Complete!{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print()
    print(f"Output directory: {output_dir}")
    print()
    print("Next steps:")
    print(f"  1. Copy output/{Colors.OKCYAN}<node_name>{Colors.ENDC} folder to respective PC")
    print(f"  2. Copy the {Colors.OKCYAN}app/{Colors.ENDC} folder to each node output folder")
    print(f"  3. Run {Colors.OKCYAN}federation_setup.bat{Colors.ENDC} as Administrator")
    print(f"  4. Run {Colors.OKCYAN}start.bat{Colors.ENDC} to start containers")
    print()

if __name__ == "__main__":
    main()
