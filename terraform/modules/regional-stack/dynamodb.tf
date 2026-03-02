# DynamoDB table for storing greeting logs

resource "aws_dynamodb_table" "greeting_logs" {
  name         = "GreetingLogs-${var.region}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  range_key    = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Name        = "GreetingLogs-${var.region}"
    Region      = var.region
    Environment = "production"
  }
}
