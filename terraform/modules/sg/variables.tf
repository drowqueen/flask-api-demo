variable "name" {
  type = string
}

variable "description" {
  type    = string
  default = ""
}

variable "use_name_prefix" {
  type    = bool
  default = false
}

variable "vpc_id" {
  type = string
}

variable "ingress_cidr_blocks" {
  type    = list(string)
  default = []
}

variable "ingress_with_cidr_blocks" {
  type    = list(map(string))
  default = []
}

variable "ingress_rules" {
  type    = list(string)
  default = []
}

variable "egress_cidr_blocks" {
  type    = list(string)
  default = []
}

variable "egress_with_cidr_blocks" {
  type    = list(map(string))
  default = []
}

variable "egress_rules" {
  type    = list(string)
  default = []
}

variable "tags" {
  type = map(string)
  default = {
    Owner = "Terragrunt"
  }
}
