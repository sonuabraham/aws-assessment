# Multi-Region AWS Infrastructure

This Terraform configuration deploys a multi-region AWS infrastructure with:

- Centralized Cognito User Pool in us-east-1
- Regional compute stacks in us-east-1 and eu-west-1
- Test SNS topics for verification

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- AWS account with permissions to create the required resources

## Quick Start

1. Copy the example variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your values:

```hcl
user_email = "your-email@example.com"
user_password = "YourSecurePassword123!"
github_repo = "https://github.com/your-username/your-repo"
subscribe_to_sns = false  # Set to true to receive test notifications
```

3. Initialize Terraform:

```bash
terraform init
```

4. Review the deployment plan:

```bash
terraform plan
```

5. Deploy the infrastructure:

```bash
terraform apply
```

## SNS Topics

The configuration creates test SNS topics in us-east-1:

- `test-lambda-verification-topic` - For Lambda function verification
- `test-ecs-verification-topic` - For ECS task verification

### Email Subscriptions (Optional)

If you set `subscribe_to_sns = true`, you'll receive a confirmation email for each SNS topic. You must confirm these subscriptions to receive notifications.

### Using Production SNS Topics

When you're ready to use the actual production SNS topics, you can modify the configuration:

1. Update `terraform/main.tf` to use external SNS topic ARNs instead of the module
2. Or modify the SNS module to use data sources to reference existing topics

## Outputs

After deployment, Terraform will output:

- Cognito User Pool details (ID, ARN, Client ID, Endpoint)
- API Gateway endpoints for both regions
- DynamoDB table names
- ECS cluster names
- SNS topic ARNs

View outputs:

```bash
terraform output
```

## Testing

Use the test configuration output to test the deployed infrastructure:

```bash
terraform output test_configuration
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         us-east-1                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Cognito    │  │  SNS Topics  │  │ Regional     │     │
│  │  User Pool   │  │   (Test)     │  │   Stack      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                        │                     │
│                                        ├─ API Gateway       │
│                                        ├─ Lambda Functions  │
│                                        ├─ ECS Cluster       │
│                                        └─ DynamoDB          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         eu-west-1                            │
│                     ┌──────────────┐                        │
│                     │ Regional     │                        │
│                     │   Stack      │                        │
│                     └──────────────┘                        │
│                      │                                       │
│                      ├─ API Gateway                         │
│                      ├─ Lambda Functions                    │
│                      ├─ ECS Cluster                         │
│                      └─ DynamoDB                            │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

- `modules/cognito/` - Cognito User Pool configuration
- `modules/sns/` - Test SNS topics
- `modules/regional-stack/` - Regional compute stack (API Gateway, Lambda, ECS, DynamoDB)
