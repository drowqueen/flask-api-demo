output "instance_id" {
  description = "List of IDs of the EC2 instances"
  value       = [for instance in module.ec2_instance : instance.id]
}

output "public_ip" {
  description = "List of public IP addresses of the EC2 instances, if assigned"
  value       = var.associate_public_ip_address ? [for instance in module.ec2_instance : instance.public_ip] : ["No public IP assigned"]
}

output "private_ip" {
  description = "List of private IP addresses of the EC2 instances"
  value       = [for instance in module.ec2_instance : instance.private_ip]
}

output "network_interface_id" {
  description = "The primary network interface ID of the NAT instance"
  value       = module.ec2_instance[0].primary_network_interface_id
}
