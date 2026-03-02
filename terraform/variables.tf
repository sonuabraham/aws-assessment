# Global Variables for Multi-Region Infrastructure

variable "user_email" {
  description = "Email address for Cognito test user and SNS notifications"
  type        = string
  default     = "sonuabraham2001@gmail.com"
}

variable "user_password" {
  description = "Password for Cognito test user"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository URL for verification payload"
  type        = string
  default     = "https://github.com/sonuabraham/aws-assessment"
}

variable "sns_topic_arn_lambda" {
  description = "External SNS topic ARN for Lambda verification"
  type        = string
  default     = "arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic1"
}

variable "sns_topic_arn_ecs" {
  description = "External SNS topic ARN for ECS verification"
  type        = string
  default     = "arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic1"
}
