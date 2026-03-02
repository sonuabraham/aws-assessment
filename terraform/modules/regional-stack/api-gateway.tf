# HTTP API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = "api-${var.region}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 300
  }

  tags = {
    Name   = "api-${var.region}"
    Region = var.region
  }
}

# JWT Authorizer using Cognito User Pool
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.main.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [var.cognito_user_pool_client_id]
    issuer   = "https://cognito-idp.us-east-1.amazonaws.com/${var.cognito_user_pool_id}"
  }
}

# Integration for Greeter Lambda
resource "aws_apigatewayv2_integration" "greeter" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.greeter.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# Route for /greet endpoint
resource "aws_apigatewayv2_route" "greet" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "POST /greet"
  target             = "integrations/${aws_apigatewayv2_integration.greeter.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# Integration for Dispatcher Lambda
resource "aws_apigatewayv2_integration" "dispatcher" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.dispatcher.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# Route for /dispatch endpoint
resource "aws_apigatewayv2_route" "dispatch" {
  api_id             = aws_apigatewayv2_api.main.id
  route_key          = "POST /dispatch"
  target             = "integrations/${aws_apigatewayv2_integration.dispatcher.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# API Stage
resource "aws_apigatewayv2_stage" "production" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = {
    Name   = "api-stage-${var.region}"
    Region = var.region
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/api-${var.region}"
  retention_in_days = 7

  tags = {
    Name   = "api-gateway-logs-${var.region}"
    Region = var.region
  }
}

# Lambda Permission for Greeter
resource "aws_lambda_permission" "greeter_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.greeter.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# Lambda Permission for Dispatcher
resource "aws_lambda_permission" "dispatcher_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dispatcher.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
