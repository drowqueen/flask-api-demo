data "aws_ssm_parameter" "ami" {
  count = var.ami_ssm_parameter != null ? 1 : 0
  name  = var.ami_ssm_parameter
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "5.7.1"

  count                       = var.instance_count
  name                        = "${var.name}-${count.index + 1}"
  ami                         = var.ami_ssm_parameter != null ? data.aws_ssm_parameter.ami[0].value : var.ami_id
  availability_zone           = var.availability_zone
  instance_type               = var.instance_type
  iam_instance_profile        = var.iam_instance_profile
  key_name                    = var.key_name
  monitoring                  = var.monitoring
  vpc_security_group_ids      = var.vpc_security_group_ids
  subnet_id                   = var.subnet_id
  associate_public_ip_address = var.associate_public_ip_address

  # Enforce IMDSv2
  metadata_options = {
    http_endpoint               = "enabled"
    http_tokens                = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }

  root_block_device = var.root_block_device != null ? var.root_block_device : [{
    volume_type = "gp2"
    volume_size = 8
  }]

  tags = merge(
    var.tags,
    try(var.instance_tags[tostring(count.index)], {})
  )
}