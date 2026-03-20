#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
deploy.py

Auto-deploy configuration files to all nodes in the cluster.
Supports deployment via:
1. Manual copy (generate deployment package)
2. SCP (Linux/WSL)
3. PsExec (Windows - requires PsExec installed)
4. WinRM (Windows - requires pywinrm)

Usage:
    python scripts/deploy.py [--method <manual|scp|psexec|winrm>]

Options:
    --method manual   Generate deployment package (default)
    --method scp      Deploy via SCP (Linux/WSL)
    --method psexec   Deploy via PsExec (Windows)
    --method winrm    Deploy via WinRM (Windows)

Example:
    python scripts/deploy.py --method manual
    python scripts/deploy.py --method scp --user admin --password secret
"""

import json
import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

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

def create_deployment_package(config, output_dir, deploy_dir):
    """Create deployment package for manual copy"""
    
    print(f"\n{Colors.OKCYAN}Creating deployment package...{Colors.ENDC}")
    
    # Create main deployment directory
    os.makedirs(deploy_dir, exist_ok=True)
    
    # Copy app folder to deployment package
    app_source = os.path.join(os.path.dirname(output_dir), 'A')
    app_dest = os.path.join(deploy_dir, 'app')
    
    if os.path.exists(app_source):
        print(f"  Copying app folder...")
        if os.path.exists(app_dest):
            shutil.rmtree(app_dest)
        shutil.copytree(app_source, app_dest)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} App folder copied")
    else:
        print(f"  {Colors.WARNING}⚠{Colors.ENDC} App folder not found, skipping...")
    
    # Copy Dockerfile
    dockerfile_source = os.path.join(os.path.dirname(output_dir), 'Dockerfile')
    dockerfile_dest = os.path.join(deploy_dir, 'Dockerfile')
    if os.path.exists(dockerfile_source):
        shutil.copy2(dockerfile_source, dockerfile_dest)
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Dockerfile copied")
    
    # Copy each node's output folder
    enabled_nodes = [n for n in config['nodes'] if n.get('enabled', True)]
    
    for node in enabled_nodes:
        node_source = os.path.join(output_dir, node['name'])
        node_dest = os.path.join(deploy_dir, node['name'])
        
        if not os.path.exists(node_source):
            print(f"  {Colors.WARNING}⚠{Colors.ENDC} Skipping {node['name']} - not generated yet")
            continue
        
        print(f"  Preparing {node['name']}...")
        
        # Create node destination
        if os.path.exists(node_dest):
            shutil.rmtree(node_dest)
        shutil.copytree(node_source, node_dest)
        
        # Copy app folder to node directory
        node_app_dest = os.path.join(node_dest, 'app')
        if os.path.exists(app_source) and not os.path.exists(node_app_dest):
            shutil.copytree(app_source, node_app_dest)
        
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {node['name']} ready")
    
    # Create deployment instructions
    instructions_file = os.path.join(deploy_dir, 'DEPLOYMENT_INSTRUCTIONS.txt')
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DEPLOYMENT INSTRUCTIONS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Nodes: {len(enabled_nodes)}\n\n")
        
        f.write("STEP 1: Copy Folder to Each PC\n")
        f.write("-" * 40 + "\n")
        f.write("Copy the entire '{}' folder to a USB drive or network share.\n\n".format(os.path.basename(deploy_dir)))
        
        f.write("STEP 2: For Each PC\n")
        f.write("-" * 40 + "\n")
        for node in enabled_nodes:
            f.write(f"\n--- {node['name'].upper()} ({node['ip']}) ---\n")
            f.write(f"1. Copy folder '{node['name']}' to PC at: {node['location']}\n")
            f.write(f"2. IP Address should be: {node['ip']}\n")
            f.write(f"3. Open Command Prompt as Administrator\n")
            f.write(f"4. Navigate to folder and run:\n")
            f.write(f"   cd {node['name']}\n")
            f.write(f"   federation_setup.bat\n")
            f.write(f"5. After federation setup completes, run:\n")
            f.write(f"   start.bat\n")
            f.write(f"6. Verify with:\n")
            f.write(f"   verify_federation.bat\n")
            f.write(f"7. Access RabbitMQ UI: http://{node['ip']}:{config['management_port']}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("DEPLOYMENT COMPLETE\n")
        f.write("=" * 80 + "\n")
    
    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Deployment instructions created")
    
    print(f"\n{Colors.OKGREEN}✓ Deployment package created: {deploy_dir}{Colors.ENDC}")
    
    return deploy_dir

def deploy_via_scp(config, output_dir, username, password):
    """Deploy via SCP (Linux/WSL)"""
    
    print(f"\n{Colors.OKCYAN}Deploying via SCP...{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠{Colors.ENDC} This feature requires SCP and SSH access to target machines")
    
    enabled_nodes = [n for n in config['nodes'] if n.get('enabled', True)]
    
    for node in enabled_nodes:
        print(f"\nDeploying to {node['name']} ({node['ip']})...")
        
        node_source = os.path.join(output_dir, node['name'])
        
        if not os.path.exists(node_source):
            print(f"  {Colors.FAIL}✗{Colors.ENDC} Source folder not found")
            continue
        
        # SCP command
        scp_cmd = f"scp -r {node_source}/* {username}@{node['ip']}:/opt/chat_app/"
        print(f"  Command: {scp_cmd}")
        
        try:
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Deployed successfully")
            else:
                print(f"  {Colors.FAIL}✗{Colors.ENDC} Failed: {result.stderr}")
        except Exception as e:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} Error: {e}")
    
    print(f"\n{Colors.WARNING}⚠{Colors.ENDC} SCP deployment complete (check errors above)")

def deploy_via_psexec(config, output_dir, username, password):
    """Deploy via PsExec (Windows)"""
    
    print(f"\n{Colors.OKCYAN}Deploying via PsExec...{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠{Colors.ENDC} This feature requires PsExec from Sysinternals")
    print(f"{Colors.WARNING}⚠{Colors.ENDC} Download from: https://docs.microsoft.com/en-us/sysinternals/downloads/psexec")
    
    enabled_nodes = [n for n in config['nodes'] if n.get('enabled', True)]
    
    for node in enabled_nodes:
        print(f"\nDeploying to {node['name']} ({node['ip']})...")
        
        node_source = os.path.join(output_dir, node['name'])
        
        if not os.path.exists(node_source):
            print(f"  {Colors.FAIL}✗{Colors.ENDC} Source folder not found")
            continue
        
        print(f"  {Colors.WARNING}⚠{Colors.ENDC} Manual copy required - PsExec automation not fully implemented")
        print(f"  Please copy {node_source} to \\\\{node['ip']}\\share\\")
    
    print(f"\n{Colors.WARNING}⚠{Colors.ENDC} PsExec deployment requires manual file copy")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Deploy RabbitMQ Federation config to all nodes')
    parser.add_argument('--method', choices=['manual', 'scp', 'psexec', 'winrm'], 
                       default='manual', help='Deployment method (default: manual)')
    parser.add_argument('--user', default='', help='Username for SCP/WinRM')
    parser.add_argument('--password', default='', help='Password for SCP/WinRM')
    parser.add_argument('--deploy-dir', default='', help='Custom deployment directory')
    
    args = parser.parse_args()
    
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}  RabbitMQ Federation Deployment Tool{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print()
    
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, 'config', 'network_config.json')
    output_dir = os.path.join(project_root, 'output')
    
    # Set deployment directory
    if args.deploy_dir:
        deploy_dir = args.deploy_dir
    else:
        deploy_dir = os.path.join(project_root, 'deployment_package')
    
    print(f"{Colors.OKBLUE}Config file:{Colors.ENDC} {config_path}")
    print(f"{Colors.OKBLUE}Output directory:{Colors.ENDC} {output_dir}")
    print(f"{Colors.OKBLUE}Deployment method:{Colors.ENDC} {args.method}")
    print(f"{Colors.OKBLUE}Deployment directory:{Colors.ENDC} {deploy_dir}")
    print()
    
    # Load configuration
    print(f"{Colors.OKCYAN}Loading configuration...{Colors.ENDC}")
    config = load_config(config_path)
    print(f"{Colors.OKGREEN}✓ Loaded {len(config['nodes'])} nodes from config{Colors.ENDC}")
    print()
    
    # Check if output exists
    if not os.path.exists(output_dir):
        print(f"{Colors.FAIL}❌ Output directory not found!{Colors.ENDC}")
        print(f"Please run generate scripts first:")
        print(f"  python scripts/generate_federation.py")
        print(f"  python scripts/generate_docker_compose.py")
        sys.exit(1)
    
    # Deploy based on method
    if args.method == 'manual':
        create_deployment_package(config, output_dir, deploy_dir)
        
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✓ Deployment Package Ready!{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print()
        print(f"Package location: {deploy_dir}")
        print()
        print("Next steps:")
        print(f"  1. Copy '{os.path.basename(deploy_dir)}' folder to USB drive or network share")
        print(f"  2. Distribute to each PC according to DEPLOYMENT_INSTRUCTIONS.txt")
        print(f"  3. On each PC, run federation_setup.bat as Administrator")
        print(f"  4. Then run start.bat")
        print()
        
    elif args.method == 'scp':
        if not args.user:
            print(f"{Colors.FAIL}❌ Username required for SCP!{Colors.ENDC}")
            print(f"Usage: python scripts/deploy.py --method scp --user <username> --password <password>")
            sys.exit(1)
        deploy_via_scp(config, output_dir, args.user, args.password)
        
    elif args.method == 'psexec':
        deploy_via_psexec(config, output_dir, args.user, args.password)
        
    elif args.method == 'winrm':
        print(f"{Colors.FAIL}❌ WinRM deployment not yet implemented!{Colors.ENDC}")
        print(f"Please use --method manual for now")
        sys.exit(1)

if __name__ == "__main__":
    main()
