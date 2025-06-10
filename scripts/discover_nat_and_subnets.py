#!/usr/bin/env python3

import boto3
import os

REGION = os.environ.get("AWS_REGION", "eu-west-1")

def get_nat_instance(ec2):
    filters = [
        {"Name": "tag:Role", "Values": ["nat"]},
        {"Name": "instance-state-name", "Values": ["running"]},
    ]
    resp = ec2.describe_instances(Filters=filters)
    for reservation in resp["Reservations"]:
        for instance in reservation["Instances"]:
            return instance
    return None

def get_subnets_by_tag(ec2, tag_key, tag_value):
    filters = [
        {"Name": f"tag:{tag_key}", "Values": [tag_value]},
    ]
    resp = ec2.describe_subnets(Filters=filters)
    return resp["Subnets"]

def print_subnets(subnets, label):
    if subnets:
        vpc_id = subnets[0]["VpcId"]
        print(f"{label} (VPC: {vpc_id}): {[s['SubnetId'] for s in subnets]}")
        return vpc_id
    else:
        print(f"{label}: []")
        return None

def main():
    ec2 = boto3.client("ec2", region_name=REGION)

    # NAT instance
    nat_instance = get_nat_instance(ec2)
    vpc_id = None
    if nat_instance:
        nat_subnet_id = nat_instance["SubnetId"]
        # Get the subnet to find the VPC ID
        subnet = ec2.describe_subnets(SubnetIds=[nat_subnet_id])["Subnets"][0]
        vpc_id = subnet["VpcId"]
        print(f"NAT Instance ID: {nat_instance['InstanceId']}, Subnet ID: {nat_subnet_id}, VPC ID: {vpc_id}")
    else:
        print("No NAT instance found with tag Role=nat")

    # Private/backend subnets
    backend_subnets = get_subnets_by_tag(ec2, "Role", "backend")
    if not backend_subnets:
        backend_subnets = get_subnets_by_tag(ec2, "Role", "private")
    vpc_id_backend = print_subnets(backend_subnets, "Backend/Private Subnets")

    # Database subnets
    db_subnets = get_subnets_by_tag(ec2, "Role", "database")
    vpc_id_db = print_subnets(db_subnets, "Database Subnets")

    # Public subnets
    public_subnets = get_subnets_by_tag(ec2, "Role", "public")
    vpc_id_public = print_subnets(public_subnets, "Public Subnets")

    # Print VPC ID summary if found
    if vpc_id:
        print(f"VPC ID (from NAT instance): {vpc_id}")
    elif vpc_id_backend:
        print(f"VPC ID (from backend/private subnet): {vpc_id_backend}")
    elif vpc_id_db:
        print(f"VPC ID (from database subnet): {vpc_id_db}")
    elif vpc_id_public:
        print(f"VPC ID (from public subnet): {vpc_id_public}")
    else:
        print("VPC ID could not be determined.")

if __name__ == "__main__":
    main()