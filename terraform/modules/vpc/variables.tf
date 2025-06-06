variable "name" {
  type    = string
  default = ""
}

variable "cidr" {
  type = string
}

variable "azs" {
  type = list(string)
}

variable "private_subnets" {
  type = list(string)
  default = []
}

variable "public_subnets" {
  type    = list(string)
  default = []
}

variable "database_subnets" {
  type    = list(string)
  default = []
}
variable "enable_nat_gateway" {
  type    = bool
  default = false
}

variable "enable_vpn_gateway" {
  type    = bool
  default = false
}

variable "one_nat_gateway_per_az" {
  type    = bool
  default = false
}

variable "single_nat_gateway" {
  type    = bool
  default = false
}

variable "tags" {
  type = map(string)
  default = {
    Owner = "terragrunt"
  }
}

variable "map_public_ip_on_launch" {
  type    = bool
  default = false
}

variable "reuse_nat_ips" {
  type    = bool
  default = false
}

variable "external_nat_ip_ids" {
  type    = list(any)
  default = []
}
