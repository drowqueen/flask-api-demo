module "ec2_instance" {
  source = "terraform-aws-modules/ec2-instance/aws"

  name                        = var.name
  ami                         = var.ami
  availability_zone           = var.availability_zone
  instance_type               = var.instance_type
  key_name                    = var.key_name
  monitoring                  = var.monitoring
  vpc_security_group_ids      = var.vpc_security_group_ids
  subnet_id                   = var.subnet_id
  associate_public_ip_address = var.associate_public_ip_address
  tags                        = var.tags
}
