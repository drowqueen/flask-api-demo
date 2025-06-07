module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name                    = var.name
  cidr                    = var.cidr
  azs                     = var.azs
  private_subnets         = var.private_subnets
  public_subnets          = var.public_subnets
  database_subnets        = var.database_subnets
  enable_nat_gateway      = var.enable_nat_gateway
  enable_vpn_gateway      = var.enable_vpn_gateway
  one_nat_gateway_per_az  = var.one_nat_gateway_per_az
  single_nat_gateway      = var.single_nat_gateway
  map_public_ip_on_launch = var.map_public_ip_on_launch
  tags                    = var.tags
}

