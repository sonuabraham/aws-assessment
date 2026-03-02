# Archive Greeter Lambda function code
data "archive_file" "greeter_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions/greeter"
  output_path = "${path.module}/lambda_functions/greeter.zip"
}

# Greeter Lambda Function
resource "aws_lambda_function" "greeter" {
  filename         = data.archive_file.greeter_lambda.output_path
  function_name    = "greeter-${var.region}"
  role             = aws_iam_role.greeter_lambda.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.greeter_lambda.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.greeting_logs.name
      SNS_TOPIC_ARN  = var.sns_topic_arn_lambda
      USER_EMAIL     = var.user_email
      GITHUB_REPO    = var.github_repo
    }
  }

  tags = {
    Name   = "greeter-${var.region}"
    Region = var.region
  }
}

# Archive Dispatcher Lambda function code
data "archive_file" "dispatcher_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_functions/dispatcher"
  output_path = "${path.module}/lambda_functions/dispatcher.zip"
}

# Dispatcher Lambda Function
resource "aws_lambda_function" "dispatcher" {
  filename         = data.archive_file.dispatcher_lambda.output_path
  function_name    = "dispatcher-${var.region}"
  role             = aws_iam_role.dispatcher_lambda.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.dispatcher_lambda.output_base64sha256
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      ECS_CLUSTER     = aws_ecs_cluster.main.arn
      TASK_DEFINITION = aws_ecs_task_definition.main.arn
      SUBNET_IDS      = join(",", aws_subnet.public[*].id)
      SECURITY_GROUP  = aws_security_group.ecs_tasks.id
    }
  }

  tags = {
    Name   = "dispatcher-${var.region}"
    Region = var.region
  }
}
