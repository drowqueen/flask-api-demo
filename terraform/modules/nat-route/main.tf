resource "aws_route" "private_nat_route" {
  for_each = toset(var.private_subnet_ids) # Use the list of private subnets to create routes

  route_table_id         = var.route_table_ids[0] # Assuming route_table_ids is a list and this is the correct index
  destination_cidr_block = "0.0.0.0/0"            # Route all traffic to the NAT instance for internet access

  # Correctly use the network_interface_id of the NAT instance
  network_interface_id = var.network_interface_id # This should be the ENI ID of your NAT instance
}
