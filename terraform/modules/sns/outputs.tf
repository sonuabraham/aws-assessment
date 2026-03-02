output "lambda_topic_arn" {
  description = "ARN of the Lambda verification SNS topic"
  value       = aws_sns_topic.lambda_verification.arn
}

output "ecs_topic_arn" {
  description = "ARN of the ECS verification SNS topic"
  value       = aws_sns_topic.ecs_verification.arn
}

output "lambda_topic_name" {
  description = "Name of the Lambda verification SNS topic"
  value       = aws_sns_topic.lambda_verification.name
}

output "ecs_topic_name" {
  description = "Name of the ECS verification SNS topic"
  value       = aws_sns_topic.ecs_verification.name
}
