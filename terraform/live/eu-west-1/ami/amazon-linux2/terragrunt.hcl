include {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "${get_parent_terragrunt_dir("root")}/..//modules/ami"
}

inputs = {
  ami_name_filter = "amzn2-ami-hvm-*-x86_64-gp2"
  ami_architecture = "x86_64"
}


