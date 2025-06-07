#!/usr/bin/env python3
import json
import subprocess
import os
import sys
import yaml
import argparse

def run_aws_command(command):
    """Run an AWS CLI command and return the parsed JSON output."""
    try:
        print(f"DEBUG: Executing AWS CLI command: {' '.join(command)}", file=sys.stderr)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running AWS CLI command: {e.stderr}", file=sys.stderr)
        print(f"Command: {' '.join(command)}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing AWS CLI output: {e}", file=sys.stderr)
        print(f"Output: {result.stdout}", file=sys.stderr)
        sys.exit(1)

def get_jump_host_ip(region, jump_host_tag):
    """Fetch the public IP and DNS name of the jump host based on its tag."""
    print(f"DEBUG: Querying jump host with tag Name={jump_host_tag} in region {region}", file=sys.stderr)
    command = [
        "aws", "ec2", "describe-instances",
        "--region", region,
        "--filters", f"Name=tag:Name,Values={jump_host_tag}", "Name=instance-state-name,Values=running",
        "--query", "Reservations[].Instances[].[InstanceId,PublicIpAddress,PrivateIpAddress,PublicDnsName]",
        "--output", "json"
    ]
    instances = run_aws_command(command)
    if not instances:
        print(f"Error: No instances found with tag Name={jump_host_tag} in region {region}", file=sys.stderr)
        debug_command = [
            "aws", "ec2", "describe-instances",
            "--region", region,
            "--filters", "Name=instance-state-name,Values=running",
            "--query", "Reservations[].Instances[].[InstanceId,PublicIpAddress,PrivateIpAddress,Tags]",
            "--output", "json"
        ]
        debug_instances = run_aws_command(debug_command)
        print(f"DEBUG: All running instances in {region}:\n{json.dumps(debug_instances, indent=2)}", file=sys.stderr)
        sys.exit(1)
    
    instance_id, public_ip, private_ip, public_dns = instances[0]
    if not public_ip or not public_dns:
        print(f"Error: Jump host {instance_id} has no public IP or DNS", file=sys.stderr)
        sys.exit(1)
    
    print(f"DEBUG: Found jump host: ID={instance_id}, PublicIP={public_ip}, PrivateIP={private_ip}, PublicDNS={public_dns}", file=sys.stderr)
    return instance_id, public_ip, private_ip, public_dns

def get_backend_hosts(region):
    """Fetch private IPs, DNS names, and instance IDs of backend hosts."""
    print(f"DEBUG: Querying backend hosts in region {region} with tag Name=flask-backend-1,flask-backend-2", file=sys.stderr)
    command = [
        "aws", "ec2", "describe-instances",
        "--region", region,
        "--filters", "Name=instance-state-name,Values=running", "Name=tag:Name,Values=flask-backend-1,flask-backend-2",
        "--query", "Reservations[].Instances[].[InstanceId,PrivateIpAddress,PrivateDnsName,Tags[?Key=='Name'].Value|[0]]",
        "--output", "json"
    ]
    instances = run_aws_command(command)
    print(f"DEBUG: Found {len(instances)} backend instances: {json.dumps(instances, indent=2)}", file=sys.stderr)
    return instances

def generate_inventory():
    """Generate Ansible inventory dictionary."""
    region = os.getenv("AWS_REGION")
    if not region:
        print("Error: AWS_REGION environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    ssh_key_path = os.getenv("ANSIBLE_SSH_KEY_PATH")
    if not ssh_key_path:
        print("Error: ANSIBLE_SSH_KEY_PATH environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(ssh_key_path):
        print(f"Error: SSH key file not found at {ssh_key_path}", file=sys.stderr)
        sys.exit(1)
    
    jump_host_tag = os.getenv("JUMP_HOST_TAG", "nginx-proxy")
    backend_tag = os.getenv("BACKEND_TAG", "flask-backend")

    # Get jump host details
    jump_host_id, jump_host_public_ip, jump_host_private_ip, jump_host_dns = get_jump_host_ip(region, jump_host_tag)

    # Get backend hosts
    backend_hosts = get_backend_hosts(region)

    # Generate inventory
    inventory = {
        "all": {
            "hosts": {},
            "children": {
                "aws_ec2": {
                    "hosts": {}
                },
                f"tag_Name_{jump_host_tag.replace('-', '_')}": {
                    "hosts": {}
                },
                f"tag_Name_{backend_tag.replace('-', '_')}": {
                    "hosts": {}
                }
            }
        }
    }

    # Add jump host to inventory
    inventory["all"]["hosts"][jump_host_dns] = {
        "ansible_host": jump_host_public_ip,
        "ansible_user": "ubuntu",
        "ansible_ssh_private_key_file": ssh_key_path
    }
    inventory["all"]["children"][f"tag_Name_{jump_host_tag.replace('-', '_')}"]["hosts"][jump_host_dns] = {}
    inventory["all"]["children"]["aws_ec2"]["hosts"][jump_host_dns] = {}

    # Add backend hosts to inventory
    for instance in backend_hosts:
        instance_id, private_ip, private_dns, name_tag = instance
        if instance_id != jump_host_id:  # Exclude jump host
            inventory["all"]["hosts"][private_dns] = {
                "ansible_host": private_ip,
                "ansible_user": "ec2-user",
                "ansible_ssh_private_key_file": ssh_key_path,
                "ansible_ssh_common_args": f"-o ProxyJump=ubuntu@{jump_host_public_ip}"
            }
            inventory["all"]["children"]["aws_ec2"]["hosts"][private_dns] = {}
            inventory["all"]["children"][f"tag_Name_{backend_tag.replace('-', '_')}"]["hosts"][private_dns] = {}
            # Create specific group for each backend instance
            group_name = f"tag_Name_{name_tag.replace('-', '_')}"
            if group_name not in inventory["all"]["children"]:
                inventory["all"]["children"][group_name] = {"hosts": {}}
            inventory["all"]["children"][group_name]["hosts"][private_dns] = {}

    return inventory

def write_inventory_file(inventory, file_path="inventory.yml"):
    """Write inventory to a YAML file."""
    try:
        with open(file_path, 'w') as f:
            yaml.safe_dump(inventory, f, default_flow_style=False)
        print(f"Successfully wrote inventory to {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing inventory file {file_path}: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to generate inventory."""
    parser = argparse.ArgumentParser(description="Generate Ansible inventory")
    parser.add_argument('--list', action='store_true', help="Output JSON inventory for Ansible")
    args = parser.parse_args()

    try:
        inventory = generate_inventory()
        if args.list:
            print(json.dumps(inventory, indent=2))
        else:
            write_inventory_file(inventory, "inventory.yml")
    except Exception as e:
        print(f"Error generating inventory: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()