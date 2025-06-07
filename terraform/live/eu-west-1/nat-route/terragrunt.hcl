terraform {
  source = "../../..///modules/nat-route"
}

dependency "vpc" {
  config_path = "../flask-demo-vpc"
}

dependency "nat_instance" {
  config_path = "../ec2/nat-instance"
}

inputs = {
  route_table_ids      = dependency.vpc.outputs.private_route_table_ids
  instance_id          = dependency.nat_instance.outputs.instance_id
  network_interface_id = dependency.nat_instance.outputs.network_interface_id
}
