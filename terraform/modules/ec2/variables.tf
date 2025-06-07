variable "name" {
  description = "Name to be used on EC2 instance created"
  type        = string
  default     = "ec2-instance"
}
variable "ami_ssm_parameter" {
  description = "SSM parameter name for the AMI ID (optional)"
  type        = string
  default     = null
}

variable "ami_id" {
  description = "Direct AMI ID to use if SSM parameter is not provided (optional)"
  type        = string
  default     = null
}

variable "availability_zone" {
  description = "AZ to start the instance in"
  type        = string
}

variable "instance_type" {
  description = "The type of instance to start"
  type        = string
  default     = "t2.micro"
}

variable "iam_instance_profile" {
  description = "The type of instance to start"
  type        = string
  default     = null
}

variable "key_name" {
  description = "Key name of the Key Pair to use for the instance"
  type        = string
}

variable "monitoring" {
  description = "If true, the launched EC2 instance will have detailed monitoring enabled"
  type        = bool
  default     = false
}

variable "vpc_security_group_ids" {
  description = "A list of security group IDs to associate with"
  type        = list(string)
}

variable "subnet_id" {
  description = "The VPC Subnet ID to launch in"
  type        = string
}

variable "associate_public_ip_address" {
  description = "Whether to associate a public IP address with the instance"
  type        = bool
  default     = true
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
  default     = {}
}

variable "instance_count" {
  description = "Number of EC2 instances to create"
  type        = number
  default     = 1
}

variable "root_block_device" {
  description = "Configuration for the root block device"
  type        = list(map(string))
  default     = []
}

variable "instance_tags" {
  description = "Map of tags for each instance, keyed by count index"
  type        = map(map(string))
  default     = {}
}