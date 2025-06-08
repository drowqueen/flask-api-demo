#!/usr/bin/env python3

import boto3
import json

def get_instances_by_tag(ec2, filters):
    return ec2.instances.filter(Filters=filters)

def main():
    ec2 = boto3.resource("ec2", region_name="eu-west-1")

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
            inventory["gateway_hosts"]["hosts"].append(inst.public_ip_address)

    # Bastion hosts (nginx proxy)
    bastion_instances = get_instances_by_tag(ec2, [
        {"Name": "tag:bastion_host", "Values": ["true"]},
        {"Name": "instance-state-name", "Values": ["running"]}
    ])
    for inst in bastion_instances:
        if inst.public_ip_address:
            inventory["bastion_hosts"]["hosts"].append(inst.public_ip_address)
        if inst.private_ip_address:
            inventory["app_servers"]["hosts"].append(inst.private_ip_address)

    # Backend app servers
    backend_instances = get_instances_by_tag(ec2, [
        {"Name": "tag:Role", "Values": ["flask-backend"]},
        {"Name": "tag:app_servers", "Values": ["true"]},
        {"Name": "instance-state-name", "Values": ["running"]}
    ])
    for inst in backend_instances:
        if inst.private_ip_address:
            inventory["app_servers"]["hosts"].append(inst.private_ip_address)

    print(json.dumps(inventory, indent=2))

if __name__ == "__main__":
    main()
