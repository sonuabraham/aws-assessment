# Infrastructure Testing

This directory contains automated tests for the multi-region AWS infrastructure.

## Setup

1. Install Python dependencies:

```bash
pip3 install -r tests/requirements.txt
```

Or using a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r tests/requirements.txt
```

2. Ensure AWS credentials are configured:

```bash
aws configure
```

## Running Tests

### Prerequisites

- Infrastructure must be deployed via Terraform
- AWS credentials configured with access to the deployed resources
- Cognito user credentials (email and password)

### Run All Tests

```bash
python3 tests/test_infrastructure.py \
  --email sonuabraham2001@gmail.com \
  --password YourPassword123!
```

The script will automatically load configuration from Terraform outputs.

### Using a Config File

Alternatively, create a config file:

```json
{
  "cognito_user_pool_id": "us-east-1_xxxxx",
  "cognito_client_id": "xxxxxxxxxxxxx",
  "api_endpoint_us": "https://xxxxx.execute-api.us-east-1.amazonaws.com",
  "api_endpoint_eu": "https://xxxxx.execute-api.eu-west-1.amazonaws.com",
  "dynamodb_table_us": "GreetingLogs-us-east-1",
  "dynamodb_table_eu": "GreetingLogs-eu-west-1",
  "ecs_cluster_us": "greeter-cluster-us-east-1",
  "ecs_cluster_eu": "greeter-cluster-eu-west-1"
}
```

Then run:

```bash
python3 tests/test_infrastructure.py \
  --email sonuabraham2001@gmail.com \
  --password YourPassword123! \
  --config-file config.json
```

## What Gets Tested

The test suite validates:

1. **Cognito Authentication** - Verifies user can authenticate and receive JWT token
2. **US-EAST-1 API** - Tests /greet endpoint in us-east-1 region
3. **EU-WEST-1 API** - Tests /greet endpoint in eu-west-1 region
4. **US-EAST-1 DynamoDB** - Verifies records are written to DynamoDB
5. **EU-WEST-1 DynamoDB** - Verifies records are written to DynamoDB
6. **US-EAST-1 Dispatch** - Tests /dispatch endpoint (triggers ECS task)
7. **EU-WEST-1 Dispatch** - Tests /dispatch endpoint (triggers ECS task)

## Expected Output

```
======================================================================
Multi-Region Infrastructure Test Suite
======================================================================

=== Step 1: Authenticating with Cognito ===
✓ Successfully authenticated with Cognito
  User Pool ID: us-east-1_xxxxx

=== Step 2: Testing US-EAST-1 API Endpoint ===
  Calling: https://xxxxx.execute-api.us-east-1.amazonaws.com/greet
✓ API call successful
  Response: {
    "message": "Hello from us-east-1",
    "region": "us-east-1"
  }

...

======================================================================
Test Summary
======================================================================
✓ PASS   Authentication
✓ PASS   US-EAST-1 API
✓ PASS   EU-WEST-1 API
✓ PASS   US-EAST-1 DynamoDB
✓ PASS   EU-WEST-1 DynamoDB
✓ PASS   US-EAST-1 Dispatch
✓ PASS   EU-WEST-1 Dispatch

Total: 7/7 tests passed
======================================================================
```

## Troubleshooting

### Authentication Fails

- Verify the user exists in Cognito User Pool
- Check the password meets Cognito password policy
- Ensure the user is confirmed (check AWS Console)

### API Calls Fail

- Verify the infrastructure is deployed
- Check API Gateway endpoints are correct
- Ensure Lambda functions are deployed and have correct permissions

### DynamoDB Verification Fails

- Run the /greet endpoint first to create records
- Check DynamoDB table names match the configuration
- Verify AWS credentials have DynamoDB read permissions

### ECS Dispatch Fails

- Ensure ECS cluster and task definitions exist
- Verify VPC, subnets, and security groups are configured
- Check ECS task execution role has required permissions
