include {
  path = find_in_parent_folders()
}

terraform {
  source = "${get_parent_terragrunt_dir("root")}/..//modules/ec2"
}

dependency "vpc" {
  config_path = "../../flask-demo-vpc"
}

dependency "flask-sg" {
  config_path = "../../security-groups/flask-backend"
}

dependency "ami" {
  config_path = "../../ami/ubuntu-minimal/"
  mock_outputs = {
    ami_id = "placeholder-ami-id"
  }
}

locals {
  instance_count = 2
}

inputs = {
  name                        = "demo-backend"
  instance_type               = "t2.micro"
  ami_id                      = dependency.ami.outputs.ami_id
  availability_zone           = "eu-west-1a"
  subnet_id                   = dependency.vpc.outputs.private_subnets[0]
  vpc_security_group_ids      = [dependency.flask-sg.outputs.security_group_id]
  key_name                    = "flask-demo"
  associate_public_ip_address = false
  instance_count              = local.instance_count
  tags = {
    Environment    = "dev"
    Role           = "flask-backend"
    app_servers    = "true"
    Owner          = "terragrunt"
  }
}