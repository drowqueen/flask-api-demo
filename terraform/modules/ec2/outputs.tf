output "instance_id" {
  description = "ID of the first EC2 instance"
  value       = module.ec2_instance[0].id
}

output "public_ip" {
  description = "Public IP address of the first EC2 instance, if assigned"
  value       = var.associate_public_ip_address ? module.ec2_instance[0].public_ip : "No public IP assigned"
}

output "private_ip" {
  description = "Private IP address of the first EC2 instance"
  value       = module.ec2_instance[0].private_ip
}

output "network_interface_id" {
  description = "The primary network interface ID of the first EC2 instance"
  value       = module.ec2_instance[0].primary_network_interface_id
}
