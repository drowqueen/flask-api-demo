resource "aws_route" "private_nat_route" {
  for_each = { for idx, rt_id in var.route_table_ids : idx => rt_id }

  route_table_id         = each.value
  destination_cidr_block = "0.0.0.0/0"
  network_interface_id   = var.network_interface_id
}
