include {
  path = find_in_parent_folders()
}

terraform {
  source = "../../..//modules/nat-route"
}

dependency "vpc" {
  config_path = "../flask-demo-vpc"
}

dependency "nat_instance" {
  config_path = "../ec2/nat-instance"
}

inputs = {
  route_table_ids = concat(
    dependency.vpc.outputs.private_route_table_ids,
    try(dependency.vpc.outputs.database_route_table_ids, [])
  )
  network_interface_id = dependency.nat_instance.outputs.network_interface_id
}