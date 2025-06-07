include {
  path = find_in_parent_folders()
}

terraform {
  source = "../../..//modules/vpc"
}


inputs = {
  name                           = "flask-demo-vpc"
  cidr                           = "10.0.0.0/16"
  private_subnets                 = [
    "10.0.1.0/24",  # eu-west-1a
    "10.0.2.0/24",  # eu-west-1b
    "10.0.3.0/24"   # eu-west-1c
  ]
  public_subnets = [
    "10.0.101.0/24",  # eu-west-1a
    "10.0.102.0/24",  # eu-west-1b
    "10.0.103.0/24"   # eu-west-1c
  ]
  map_public_ip_on_launch = true
  enable_dns_hostnames   = true
  enable_dns_support     = true
  tags = {
    "Owner" = "terragrunt",
    "Env"    = "dev"
  }
}
