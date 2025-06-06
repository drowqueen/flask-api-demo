output "instance_id" {
  description = "ID of the EC2 instance"
  value       = module.ec2_instance.id
}

output "public_ip" {
  description = "The public IP address of the EC2 instance, if assigned"
  value       = var.associate_public_ip_address ? module.ec2_instance.public_ip : "No public IP assigned"
}

output "private_ip" {
  description = "The private IP address of the EC2 instance"
  value       = module.ec2_instance.private_ip
}