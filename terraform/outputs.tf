# Root Module Outputs
# Exposes API endpoints and Cognito details for testing

# Cognito Outputs
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID in us-east-1"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN"
  value       = module.cognito.user_pool_arn
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID for authentication"
  value       = module.cognito.user_pool_client_id
}

output "cognito_user_pool_endpoint" {
  description = "Cognito User Pool endpoint"
  value       = module.cognito.user_pool_endpoint
}

# US-East-1 Regional Outputs
output "api_endpoint_us_east_1" {
  description = "API Gateway endpoint URL for us-east-1"
  value       = module.regional_stack_us.api_endpoint
}

output "dynamodb_table_us_east_1" {
  description = "DynamoDB table name in us-east-1"
  value       = module.regional_stack_us.dynamodb_table_name
}

output "ecs_cluster_us_east_1" {
  description = "ECS cluster name in us-east-1"
  value       = module.regional_stack_us.ecs_cluster_name
}

# EU-West-1 Regional Outputs
output "api_endpoint_eu_west_1" {
  description = "API Gateway endpoint URL for eu-west-1"
  value       = module.regional_stack_eu.api_endpoint
}

output "dynamodb_table_eu_west_1" {
  description = "DynamoDB table name in eu-west-1"
  value       = module.regional_stack_eu.dynamodb_table_name
}

output "ecs_cluster_eu_west_1" {
  description = "ECS cluster name in eu-west-1"
  value       = module.regional_stack_eu.ecs_cluster_name
}

# Test Configuration Output
output "test_configuration" {
  description = "Configuration values for running the test script"
  value = {
    cognito_user_pool_id = module.cognito.user_pool_id
    cognito_client_id    = module.cognito.user_pool_client_id
    api_endpoint_us      = module.regional_stack_us.api_endpoint
    api_endpoint_eu      = module.regional_stack_eu.api_endpoint
    user_email           = var.user_email
  }
}
