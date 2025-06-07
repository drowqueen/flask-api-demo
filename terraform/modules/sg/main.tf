module "security-group" {
  source                   = "terraform-aws-modules/security-group/aws"
  version                  = "~> 5.0"
  name                     = var.name
  use_name_prefix          = var.use_name_prefix
  vpc_id                   = var.vpc_id
  ingress_cidr_blocks      = var.ingress_cidr_blocks
  ingress_with_cidr_blocks = var.ingress_with_cidr_blocks
  ingress_rules            = var.ingress_rules
  egress_cidr_blocks       = var.egress_cidr_blocks
  egress_with_cidr_blocks  = var.egress_with_cidr_blocks
  egress_rules             = var.egress_rules
  tags                     = var.tags
}
