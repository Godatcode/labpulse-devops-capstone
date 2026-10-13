terraform {
  required_version = ">= 1.13.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # Plan the graph in a classroom without AWS credentials. Leave false for apply.
  skip_credentials_validation = var.offline_plan
  skip_metadata_api_check     = var.offline_plan
  skip_requesting_account_id  = var.offline_plan

  default_tags {
    tags = {
      Project   = "LabPulse"
      ManagedBy = "Terraform"
      Purpose   = "Student capstone"
    }
  }
}
