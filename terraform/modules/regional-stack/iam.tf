# IAM Role for Greeter Lambda
resource "aws_iam_role" "greeter_lambda" {
  name = "greeter-lambda-role-${var.region}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name   = "greeter-lambda-role-${var.region}"
    Region = var.region
  }
}

# Attach AWS managed policy for basic Lambda execution
resource "aws_iam_role_policy_attachment" "greeter_lambda_basic" {
  role       = aws_iam_role.greeter_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for DynamoDB PutItem
resource "aws_iam_role_policy" "greeter_dynamodb" {
  name = "greeter-dynamodb-policy"
  role = aws_iam_role.greeter_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem"
        ]
        Resource = aws_dynamodb_table.greeting_logs.arn
      }
    ]
  })
}

# Inline policy for SNS Publish
resource "aws_iam_role_policy" "greeter_sns" {
  name = "greeter-sns-policy"
  role = aws_iam_role.greeter_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = var.sns_topic_arn_lambda
      }
    ]
  })
}

# IAM Role for Dispatcher Lambda
resource "aws_iam_role" "dispatcher_lambda" {
  name = "dispatcher-lambda-role-${var.region}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name   = "dispatcher-lambda-role-${var.region}"
    Region = var.region
  }
}

# Attach AWS managed policy for basic Lambda execution
resource "aws_iam_role_policy_attachment" "dispatcher_lambda_basic" {
  role       = aws_iam_role.dispatcher_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for ECS RunTask
resource "aws_iam_role_policy" "dispatcher_ecs" {
  name = "dispatcher-ecs-policy"
  role = aws_iam_role.dispatcher_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask"
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "ecs:cluster" = aws_ecs_cluster.main.arn
          }
        }
      }
    ]
  })
}

# Inline policy for IAM PassRole
resource "aws_iam_role_policy" "dispatcher_passrole" {
  name = "dispatcher-passrole-policy"
  role = aws_iam_role.dispatcher_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution.arn,
          aws_iam_role.ecs_task.arn
        ]
      }
    ]
  })
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecs-task-execution-role-${var.region}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name   = "ecs-task-execution-role-${var.region}"
    Region = var.region
  }
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role (for container permissions)
resource "aws_iam_role" "ecs_task" {
  name = "ecs-task-role-${var.region}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name   = "ecs-task-role-${var.region}"
    Region = var.region
  }
}

# Inline policy for ECS task to publish to SNS
resource "aws_iam_role_policy" "ecs_task_sns" {
  name = "ecs-task-sns-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = var.sns_topic_arn_ecs
      }
    ]
  })
}
