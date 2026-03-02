# Multi-Region AWS Infrastructure
# This configuration deploys a centralized Cognito User Pool in us-east-1
# and identical compute stacks in both us-east-1 and eu-west-1

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Primary provider for us-east-1 (Cognito + Regional Stack)
provider "aws" {
  region = "us-east-1"
  alias  = "us_east_1"
}

# Secondary provider for eu-west-1 (Regional Stack only)
provider "aws" {
  region = "eu-west-1"
  alias  = "eu_west_1"
}

# Cognito module (us-east-1 only)
module "cognito" {
  source = "./modules/cognito"
  providers = {
    aws = aws.us_east_1
  }

  user_email    = var.user_email
  user_password = var.user_password
}

# Regional stack for us-east-1
module "regional_stack_us" {
  source = "./modules/regional-stack"
  providers = {
    aws = aws.us_east_1
  }

  region                = "us-east-1"
  cognito_user_pool_arn = module.cognito.user_pool_arn
  sns_topic_arn_lambda  = var.sns_topic_arn_lambda
  sns_topic_arn_ecs     = var.sns_topic_arn_ecs
  user_email            = var.user_email
  github_repo           = var.github_repo
}

# Regional stack for eu-west-1
module "regional_stack_eu" {
  source = "./modules/regional-stack"
  providers = {
    aws = aws.eu_west_1
  }

  region                = "eu-west-1"
  cognito_user_pool_arn = module.cognito.user_pool_arn
  sns_topic_arn_lambda  = var.sns_topic_arn_lambda
  sns_topic_arn_ecs     = var.sns_topic_arn_ecs
  user_email            = var.user_email
  github_repo           = var.github_repo
}
