variable "notification_email" {
  description = "Email address for SNS topic subscriptions"
  type        = string
}

variable "subscribe_email" {
  description = "Whether to subscribe email to SNS topics"
  type        = bool
  default     = false
}
