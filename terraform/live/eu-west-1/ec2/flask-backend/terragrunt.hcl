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

inputs = {
  name                        = "demo-backend"
  instance_type               = "t2.micro"
  ami_ssm_parameter           = "/flask-demo/backend/latest-ami"
  availability_zone           = "eu-west-1a"
  subnet_id                   = dependency.vpc.outputs.public_subnets[0]
  vpc_security_group_ids      = [dependency.flask-sg.outputs.security_group_id]
  key_name                    = "flask-demo"
  associate_public_ip_address = false
  instance_count              = 2
  root_block_device = [{
    volume_size           = 16
    volume_type           = "gp3"
    delete_on_termination = true
  }]
  tags = {
    Owner = "terragrunt"
    Env   = "dev"
  }
  instance_tags = {
    "0" = {
      Name = "flask-backend-1"
    }
    "1" = {
      Name = "flask-backend-2"
    }
  }
}