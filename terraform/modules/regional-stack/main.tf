# Regional Stack Module
# This module provisions the complete compute stack for a single region
# including API Gateway, Lambda, DynamoDB, and ECS Fargate resources

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data source to get available AZs in the region
data "aws_availability_zones" "available" {
  state = "available"
}
