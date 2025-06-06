include {
  path = find_in_parent_folders()
}

terraform {
  source = "../../..//modules/vpc"
}


inputs = {
  name                           = "flask-demo-vpc"
  cidr                           = "10.0.0.0/16"
  public_subnets                 = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  tags = {
    "Owner" = "Terragrunt",
  }
}
