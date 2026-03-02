# Global Variables for Multi-Region Infrastructure

variable "user_email" {
  description = "Email address for Cognito test user and SNS notifications"
  type        = string
  default     = "sonuabraham2001@gmail.com"
}

variable "github_repo" {
  description = "GitHub repository URL for verification payload"
  type        = string
  default     = "https://github.com/sonuabraham/aws-assessment"
}

variable "sns_topic_arn" {
  description = "External SNS topic ARN for candidate verification"
  type        = string
  default     = "arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic"
}
