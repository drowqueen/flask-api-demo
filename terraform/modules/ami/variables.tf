variable "ami_name_filter" {
  description = "The name filter for the AMI (e.g., al2023-ami-minimal-*)"
  type        = string
}

variable "ami_architecture" {
  description = "The architecture of the AMI (e.g., x86_64, arm64)"
  type        = string
  default     = "x86_64"
}

variable "ami_owners" {
  description = "List of AMI owners (e.g., amazon, self)"
  type        = list(string)
  default     = ["amazon"]
}