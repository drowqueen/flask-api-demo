include {
  path = find_in_parent_folders()
}

terraform {
  source = "${get_parent_terragrunt_dir("root")}/..//modules/sg"
}

dependency "vpc" {
  config_path = "../../flask-demo-vpc"
}

dependency "nginx-sg" {
  config_path = "../nginx-proxy"
}

inputs = {
  name        = "flask-backend"
  description = "Security group for the flask backend"
  vpc_id      = dependency.vpc.outputs.vpc_id
  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
  ingress_with_source_security_group_id = [
    {
      from_port                = 5001
      to_port                  = 5001
      protocol                 = "tcp"
      source_security_group_id = dependency.nginx-sg.outputs.security_group_id
    }
  ]
  tags = {
    "Owner" = "terragrunt",
    "Env"   = "dev"
  }
}
