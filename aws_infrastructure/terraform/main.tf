terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Plataforma-Nacional-Becas-MINEDUC"
      Environment = var.environment
      Sprint      = "Sprint-1"
      ManagedBy   = "Terraform"
    }
  }
}
