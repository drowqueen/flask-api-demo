include {
  path = find_in_parent_folders()
}

terraform {
  source = "${get_parent_terragrunt_dir("root")}/..//modules/sg"
}

dependency "vpc" {
  config_path = "../../flask-demo-vpc"
}


inputs = {
  name        = "nginx-proxy"
  description = "Security group for the nginx reverse proxy"
  vpc_id      = dependency.vpc.outputs.vpc_id
  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
  tags = {
    "Owner" = "terragrunt"
  }
}
