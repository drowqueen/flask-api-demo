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
  route_table_ids      = dependency.vpc.outputs.private_route_table_ids
  vpc_id               = dependency.vpc.outputs.vpc_id
  nat_instance_id      = dependency.nat_instance.outputs.instance_id
  network_interface_id = dependency.nat_instance.outputs.network_interface_id  
  private_subnet_ids   = dependency.vpc.outputs.private_subnets
  security_group_id    = "sg-0636b592106125ed4"
}
