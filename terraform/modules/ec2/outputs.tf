output "ec2_public_ip" {
  description = "The public IP address of the EC2 instance, if assigned"
  value       = var.associate_public_ip_address ? module.ec2_instance.public_ip : "No public IP assigned"
}