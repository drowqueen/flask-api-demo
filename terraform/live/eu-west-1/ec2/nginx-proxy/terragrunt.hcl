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
  config_path = "../../ami/amazon-linux-minimal/"
  mock_outputs = {
    ami_id = "placeholder-ami-id"
  }
}

inputs = {
  name                        = "demo-nginx-proxy"
  ami                         = dependency.ami.outputs.ami_id
  instance_type               = "t2.micro"
  availability_zone           = "eu-west-1a"
  subnet_id                   = dependency.vpc.outputs.public_subnets[0]
  vpc_security_group_ids      = [dependency.nginx-sg.outputs.security_group_id]
  key_name                    = "flask-demo"
  associate_public_ip_address = true
  tags = {
    "Name"  = "demo-backend"
    "Owner" = "terragrunt"
    "Env"   = "dev"
  }
}