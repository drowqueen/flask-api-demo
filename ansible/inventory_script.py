#!/usr/bin/env python3

import boto3
import json
import os
import sys
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
            # Return private IP for app_servers, public IP for others
            if tag_key == "app_servers":
                instances.append(instance.get("PrivateIpAddress"))
            else:
                instances.append(instance.get("PublicIpAddress"))
    return [i for i in instances if i]

def main():
    region = os.environ.get("AWS_REGION", "eu-west-1")
    ssm_param = "/flask-demo/ssh/flask-demo-key"

    # Fetch the SSH private key from SSM and save it to a temp file
    ssh_key_content = get_ssh_key_from_ssm(region, ssm_param)
    ssh_key_path = save_ssh_key_to_tempfile(ssh_key_content)

    bastion_hosts = get_instances_by_tag(region, "bastion_host")
    gateway_hosts = get_instances_by_tag(region, "gateway_hosts")
    app_servers = get_instances_by_tag(region, "app_servers")

    if not bastion_hosts:
        print("No bastion host found. Exiting.", file=sys.stderr)
        sys.exit(1)

    inventory = {
        "bastion_hosts": {
            "hosts": bastion_hosts,
            "vars": {
                "ansible_user": "ubuntu",
                "ansible_python_interpreter": "/usr/bin/python3",
                # Key is fetched and saved, but we rely on the SSH agent instead of specifying -i
            },
        },
        "gateway_hosts": {
            "hosts": gateway_hosts,
            "vars": {
                "ansible_user": "ec2-user",
                "ansible_python_interpreter": "/usr/bin/python3.8",
                # Key is fetched and saved, but agent forwarding will be used
            },
        },
        "app_servers": {
            "hosts": app_servers,
            "vars": {
                "ansible_user": "ubuntu",
                "ansible_python_interpreter": "/usr/bin/python3",  
                "ansible_ssh_common_args": (
                    f'-o StrictHostKeyChecking=no '
                    f'-o ProxyCommand="ssh -W %h:%p -q ubuntu@{bastion_hosts[0]}"'
                ),
                # No ansible_ssh_private_key_file here; SSH agent must hold the key
            },
        },
        "_meta": {"hostvars": {}},
    }

    print(json.dumps(inventory, indent=2))

if __name__ == "__main__":
    main()
