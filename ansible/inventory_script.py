#!/usr/bin/env python3

import boto3
import json

def get_instances_by_tag(ec2, filters):
    return ec2.instances.filter(Filters=filters)

def main():
    ec2 = boto3.resource("ec2", region_name="eu-west-1")

    bastion_ips = []
    gateway_ips = []
    app_private_ips = []

    inventory = {
        "gateway_hosts": {"hosts": [], "vars": {}},
        "bastion_hosts": {"hosts": [], "vars": {}},
        "app_servers": {"hosts": [], "vars": {}},
        "_meta": {"hostvars": {}}
    }

    # NAT instances (gateway_hosts)
    nat_instances = get_instances_by_tag(ec2, [
        {"Name": "tag:Role", "Values": ["flask-nat"]},
        {"Name": "tag:gateway_hosts", "Values": ["true"]},
        {"Name": "instance-state-name", "Values": ["running"]}
    ])
    for inst in nat_instances:
        if inst.public_ip_address:
            gateway_ips.append(inst.public_ip_address)

    # Bastion hosts (nginx proxy)
    bastion_instances = get_instances_by_tag(ec2, [
        {"Name": "tag:bastion_host", "Values": ["true"]},
        {"Name": "instance-state-name", "Values": ["running"]}
    ])
    for inst in bastion_instances:
        if inst.public_ip_address:
            bastion_ips.append(inst.public_ip_address)
        if inst.private_ip_address:
            app_private_ips.append(inst.private_ip_address)

    # Backend app servers
    backend_instances = get_instances_by_tag(ec2, [
        {"Name": "tag:Role", "Values": ["flask-backend"]},
        {"Name": "tag:app_servers", "Values": ["true"]},
        {"Name": "instance-state-name", "Values": ["running"]}
    ])
    for inst in backend_instances:
        if inst.private_ip_address:
            app_private_ips.append(inst.private_ip_address)

    # Assign hosts to inventory groups
    inventory["gateway_hosts"]["hosts"] = gateway_ips
    inventory["bastion_hosts"]["hosts"] = bastion_ips
    inventory["app_servers"]["hosts"] = app_private_ips

    ssh_key_path = "~/.ssh/flask-demo.pem"

    # Both gateway and bastion use ec2-user
    inventory["gateway_hosts"]["vars"] = {
        "ansible_user": "ec2-user",
        "ansible_ssh_private_key_file": ssh_key_path
    }
    inventory["bastion_hosts"]["vars"] = {
        "ansible_user": "ec2-user",
        "ansible_ssh_private_key_file": ssh_key_path
    }

    # app_servers use bastion as jump host with explicit ProxyCommand user=ec2-user and StrictHostKeyChecking=no
    if bastion_ips:
        bastion_ip = bastion_ips[0]
        proxy_cmd = (
            f"-o StrictHostKeyChecking=no "
            f"-o ProxyCommand=\"ssh -W %h:%p -q -i {ssh_key_path} ec2-user@{bastion_ip}\""
        )
    else:
        proxy_cmd = ""

    inventory["app_servers"]["vars"] = {
        "ansible_user": "ubuntu",
        "ansible_ssh_private_key_file": ssh_key_path,
        "ansible_ssh_common_args": proxy_cmd
    }

    print(json.dumps(inventory, indent=2))

if __name__ == "__main__":
    main()
