include {
  path = find_in_parent_folders("root.hcl")
}

inputs = {
  aws_region = "eu-west-1"
  azs        = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
}