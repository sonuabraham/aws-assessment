output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "" # Will be populated when API Gateway is implemented
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = "" # Will be populated when DynamoDB is implemented
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = "" # Will be populated when ECS is implemented
}
