variable "user_email" {
  description = "Email address for the test user"
  type        = string
}

variable "user_password" {
  description = "Password for the test user"
  type        = string
  sensitive   = true
}
