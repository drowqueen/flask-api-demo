output "ami_id" {
  description = "The ID of the selected AMI"
  value       = data.aws_ami.selected.id
}