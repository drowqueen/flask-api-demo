include {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "${get_parent_terragrunt_dir("root")}/..//modules/ec2"
}

dependency "vpc" {
  config_path = "../../flask-demo-vpc"
}

dependency "nginx-sg" {
  config_path = "../../security-groups/nginx-proxy"
}

dependency "ami" {
  config_path = "../../ami/ubuntu-minimal/"
  mock_outputs = {
    ami_id = "placeholder-ami-id"
  }
}

inputs = {
  name                        = "nginx-proxy-bastion"
  ami_id                      = dependency.ami.outputs.ami_id # Ubuntu 22.04 AMI
  instance_type               = "t2.micro"
  iam_instance_profile        = "flask-demo-bastion-role"
  availability_zone           = "eu-west-1a"
  subnet_id                   = dependency.vpc.outputs.public_subnets[0]
  vpc_security_group_ids      = [dependency.nginx-sg.outputs.security_group_id]
  key_name                    = "flask-demo"
  associate_public_ip_address = true
  instance_count              = 1
  tags = {
    Environment  = "dev"
    bastion_host = "true"
    Name         = "nginx-proxy-bastion"
    Owner        = "terragrunt"
  }
}