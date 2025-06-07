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

output "public_subnets" {
  description = "List of IDs of public subnets, empty if not defined"
  value       = length(var.public_subnets) > 0 ? module.vpc.public_subnets : []
}

output "private_subnets" {
  description = "List of IDs of private subnets, empty if not defined"
  value       = length(var.private_subnets) > 0 ? module.vpc.private_subnets : []
}

output "database_subnets" {
  description = "List of IDs of database subnets, empty if not defined"
  value       = length(var.database_subnets) > 0 ? module.vpc.database_subnets : []
}

output "vpc_cidr" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnets_cidr_blocks" {
  description = "List of public subnet CIDR blocks"
  value       = module.vpc.public_subnets_cidr_blocks
}

output "private_subnets_cidr_blocks" {
  description = "List of private subnet CIDR blocks"
  value       = module.vpc.private_subnets_cidr_blocks
}

output "database_subnets_cidr_blocks" {
  description = "List of database subnet CIDR blocks"
  value       = module.vpc.database_subnets_cidr_blocks
}

output "public_route_table_ids" {
  description = "List of public RTB ids"
  value       = module.vpc.public_route_table_ids
}

output "private_route_table_ids" {
  description = "List of private RTB ids"
  value       = module.vpc.private_route_table_ids
}

output "default_security_group_id" {
  description = "Default security group id"
  value       = module.vpc.default_security_group_id
}