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

variable "subscribe_to_sns" {
  description = "Whether to subscribe email to test SNS topics (requires email confirmation)"
  type        = bool
  default     = false
}

