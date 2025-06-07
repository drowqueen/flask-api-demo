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