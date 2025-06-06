output "database_subnet_arns" {
  value = module.vpc.database_subnet_arns
}

output "private_subnet_arns" {
  value = module.vpc.private_subnet_arns
}

output "public_subnet_arns" {
  value = module.vpc.public_subnet_arns
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
