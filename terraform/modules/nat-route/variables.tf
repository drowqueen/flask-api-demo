variable "route_table_ids" {
  description = "List of private route table IDs"
  type        = list(string)
}

variable "network_interface_id" {
  description = "The network interface ID of the NAT instance (eni-xxxx)"
  type        = string
  default     = ""
}
