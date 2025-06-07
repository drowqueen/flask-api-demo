resource "aws_route" "private_to_nat" {
  for_each = toset(var.route_table_ids)

  route_table_id         = each.key
  destination_cidr_block = "0.0.0.0/0"
  network_interface_id   = var.network_interface_id
}
