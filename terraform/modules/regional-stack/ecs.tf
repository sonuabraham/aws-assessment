# VPC and networking resources for ECS Fargate

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name   = "vpc-${var.region}"
    Region = var.region
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name   = "igw-${var.region}"
    Region = var.region
  }
}

# Public Subnets (2 across different AZs)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name   = "public-subnet-${var.region}-${count.index + 1}"
    Region = var.region
    Type   = "Public"
  }
}

# Route Table for Public Subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name   = "public-rt-${var.region}"
    Region = var.region
  }
}

# Route Table Association for Public Subnets
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "cluster-${var.region}"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  tags = {
    Name   = "cluster-${var.region}"
    Region = var.region
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "ecs-tasks-sg-${var.region}"
  description = "Security group for ECS Fargate tasks"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name   = "ecs-tasks-sg-${var.region}"
    Region = var.region
  }
}

# CloudWatch Log Group for ECS Tasks
resource "aws_cloudwatch_log_group" "ecs_tasks" {
  name              = "/ecs/tasks-${var.region}"
  retention_in_days = 7

  tags = {
    Name   = "ecs-tasks-logs-${var.region}"
    Region = var.region
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = "task-${var.region}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "aws-cli"
      image = "amazon/aws-cli:latest"
      command = [
        "sh",
        "-c",
        "aws sns publish --topic-arn $SNS_TOPIC_ARN --message \"{\\\"email\\\":\\\"$USER_EMAIL\\\",\\\"source\\\":\\\"ECS\\\",\\\"region\\\":\\\"$AWS_REGION\\\",\\\"repo\\\":\\\"$GITHUB_REPO\\\"}\" --region us-east-1"
      ]
      environment = [
        {
          name  = "SNS_TOPIC_ARN"
          value = var.sns_topic_arn_ecs
        },
        {
          name  = "USER_EMAIL"
          value = var.user_email
        },
        {
          name  = "GITHUB_REPO"
          value = var.github_repo
        },
        {
          name  = "AWS_REGION"
          value = var.region
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_tasks.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name   = "task-${var.region}"
    Region = var.region
  }
}
