include {
  path = find_in_parent_folders()
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
  config_path = "../../ami/amazon-linux2/"
  mock_outputs = {
    ami_id = "placeholder-ami-id"
  }
}

inputs = {
  name                     = "nat-instance"
  vpc_id                   = dependency.vpc.outputs.vpc_id
  subnet_id                = dependency.vpc.outputs.public_subnets[0]
  ami_id                   = dependency.ami.outputs.ami_id  
  ami_ssm_parameter        = null  # Explicitly disable SSM parameter
  availability_zone        = "eu-west-1a"
  instance_type            = "t2.micro"
  vpc_security_group_ids   = [dependency.vpc.outputs.default_security_group_id]
  key_name                 = "flask-demo"
  associate_public_ip      = true
  source_dest_check        = false
  key_name                 = "flask-demo"
  tags = {
    Owner = "terragrunt"
    Environment = "dev"

  }
}
