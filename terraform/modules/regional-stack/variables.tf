variable "region" {
  description = "AWS region for the regional stack"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "ARN of the Cognito User Pool from us-east-1"
  type        = string
}

variable "sns_topic_arn_lambda" {
  description = "SNS Topic ARN for Lambda verification (Candidate-Verification-Topic1)"
  type        = string
}

variable "sns_topic_arn_ecs" {
  description = "SNS Topic ARN for ECS verification (Candidate-Verification-Topic)"
  type        = string
}

variable "user_email" {
  description = "User email for SNS payload"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository URL for SNS payload"
  type        = string
}
