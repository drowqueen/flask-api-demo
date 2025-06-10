#!/usr/bin/env python3

import boto3
import json
import os
import tempfile

def get_ssh_key_from_ssm(region, parameter_name):
    ssm = boto3.client("ssm", region_name=region)
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response["Parameter"]["Value"]

def save_ssh_key_to_tempfile(key_content):
    tf = tempfile.NamedTemporaryFile(delete=False, mode="w")
    tf.write(key_content)
    tf.close()
    os.chmod(tf.name, 0o600)
    return tf.name

def get_instances_by_tag(region, tag_key):
    ec2 = boto3.client("ec2", region_name=region)
    filters = [
        {"Name": f"tag:{tag_key}", "Values": ["true"]},
        {"Name": "instance-state-name", "Values": ["running"]},
    ]
    response = ec2.describe_instances(Filters=filters)
    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance)
    return instances

def main():
    region = os.environ.get("AWS_REGION", "eu-west-1")
    ssm_param = "/flask-demo/ssh/flask-demo-key"

    # Fetch the SSH private key from SSM and save it to a temp file
    ssh_key_content = get_ssh_key_from_ssm(region, ssm_param)
    ssh_key_path = save_ssh_key_to_tempfile(ssh_key_content)

    bastion_instances = get_instances_by_tag(region, "bastion_host")
    gateway_instances = get_instances_by_tag(region, "gateway_hosts")
    app_instances = get_instances_by_tag(region, "app_servers")

    # Extract IP addresses
    bastion_hosts = []
    for inst in bastion_instances:
        public_ip = inst.get("PublicIpAddress")
        private_ip = inst.get("PrivateIpAddress")
        if public_ip:
            bastion_hosts.append({
                "ansible_host": public_ip,
                "private_ip": private_ip
            })

    gateway_hosts = []
    for inst in gateway_instances:
        public_ip = inst.get("PublicIpAddress")
        private_ip = inst.get("PrivateIpAddress")
        if public_ip:
            gateway_hosts.append({
                "ansible_host": public_ip,
                "private_ip": private_ip
            })

    app_hosts = []
    for inst in app_instances:
        private_ip = inst.get("PrivateIpAddress")
        if private_ip:
            app_hosts.append(private_ip)

    # Build inventory format
    inventory = {
        "bastion_hosts": {
            "hosts": [h["ansible_host"] for h in bastion_hosts],
            "vars": {
                "ansible_user": "ubuntu",
                "ansible_python_interpreter": "/usr/bin/python3",
            },
        },
        "gateway_hosts": {
            "hosts": [h["ansible_host"] for h in gateway_hosts],
            "vars": {
                "ansible_user": "ec2-user",
                "ansible_python_interpreter": "/usr/bin/python3.8",
            },
        },
        "app_servers": {
            "hosts": app_hosts,
            "vars": {
                "ansible_user": "ubuntu",
                "ansible_python_interpreter": "/usr/bin/python3",
                "ansible_ssh_common_args": (
                    f'-o StrictHostKeyChecking=no '
                    f'-o ProxyCommand="ssh -W %h:%p -q ubuntu@{bastion_hosts[0]["ansible_host"]}"'
                ) if bastion_hosts else "",
            },
        },
        "_meta": {
            "hostvars": {},
        },
    }

    # Add hostvars for bastion and gateway hosts
    for h in bastion_hosts:
        inventory["_meta"]["hostvars"][h["ansible_host"]] = {
            "private_ip": h["private_ip"],
            "ansible_host": h["ansible_host"],
        }
    for h in gateway_hosts:
        inventory["_meta"]["hostvars"][h["ansible_host"]] = {
            "private_ip": h["private_ip"],
            "ansible_host": h["ansible_host"],
        }
    for ip in app_hosts:
        inventory["_meta"]["hostvars"][ip] = {
            "ansible_host": ip,
        }

    # Add group var for NAT private IP if available
    if gateway_hosts:
        inventory["gateway_hosts"]["vars"]["nat_private_ip"] = gateway_hosts[0]["private_ip"]

    print(json.dumps(inventory, indent=2))

if __name__ == "__main__":
    main()