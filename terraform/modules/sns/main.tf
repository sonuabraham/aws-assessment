# SNS Topics for Testing
# Creates dummy SNS topics for Lambda and ECS verification

resource "aws_sns_topic" "lambda_verification" {
  name         = "test-lambda-verification-topic"
  display_name = "Test Lambda Verification Topic"

  tags = {
    Name        = "test-lambda-verification-topic"
    Environment = "test"
    Purpose     = "Lambda verification testing"
  }
}

resource "aws_sns_topic" "ecs_verification" {
  name         = "test-ecs-verification-topic"
  display_name = "Test ECS Verification Topic"

  tags = {
    Name        = "test-ecs-verification-topic"
    Environment = "test"
    Purpose     = "ECS verification testing"
  }
}

# Optional: Subscribe your email to receive test notifications
resource "aws_sns_topic_subscription" "lambda_email" {
  count     = var.subscribe_email ? 1 : 0
  topic_arn = aws_sns_topic.lambda_verification.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

resource "aws_sns_topic_subscription" "ecs_email" {
  count     = var.subscribe_email ? 1 : 0
  topic_arn = aws_sns_topic.ecs_verification.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
