include {
  path = find_in_parent_folders()
}

terraform {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-iam.git//modules/iam-assumable-role?ref=v5.47.0"
}
inputs = {
  create_role = true
  role_name   = "flask-demo-bastion-role"
  role_description = "IAM role for nginx proxy bastion host"

  trusted_role_services = ["ec2.amazonaws.com"]

  custom_role_policy_arns = [
    "arn:aws:iam::244923700407:policy/deployer"
  ]

  create_instance_profile = true
}