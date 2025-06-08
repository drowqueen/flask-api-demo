variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "route_table_ids" {
  description = "List of route table IDs for private subnets"
  type        = list(string)
}

variable "network_interface_id" {
  description = "The primary ENI of the NAT instance"
  type        = string
}
