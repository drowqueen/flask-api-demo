# Root terragrunt.hcl
locals {
  # Automatically load region-level variables
  region_vars = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  aws_region   = local.region_vars.locals.aws_region
}

# Generate an AWS provider block
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
  # Only these AWS Account IDs may be operated on by this template
  allowed_account_ids = ["244923700407"]
}
EOF
}

remote_state {
  backend = "s3"
  config = {
    encrypt        = true
    bucket         = "tg-state-drq"
    key = "${replace(path_relative_to_include(), "terraform/", "")}/terraform.tfstate"
    region         = local.aws_region                   
    dynamodb_table = "my-terragrunt-locks"  # Optional: For state locking
    s3_bucket_tags = {
      Owner = "Terragrunt",
    }
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

terraform {
  extra_arguments "vars" {
    commands = ["apply", "plan"]
    arguments = [
      "-lock-timeout=300s"
    ]
  }
}

# Configure root level variables that all resources can inherit. This is especially helpful with multi-account configs
# where terraform_remote_state data sources are placed directly into the modules.
inputs = merge(
  local.region_vars.locals,
)
