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
subscribe_to_sns = false  # Only used if enabling test SNS module
sns_topic_arn_lambda = "arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic"
sns_topic_arn_ecs = "arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic"
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

The configuration uses external SNS topics for verification:

- Lambda verification: `arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic`
- ECS verification: `arn:aws:sns:us-east-1:637226132752:Candidate-Verification-Topic`

### Using Test SNS Topics (Optional)

If you want to create your own test SNS topics instead of using external ones:

1. Uncomment the SNS module in `main.tf`
2. Update the regional stack modules to use `module.sns.lambda_topic_arn` and `module.sns.ecs_topic_arn`
3. Set `subscribe_to_sns = true` in terraform.tfvars to receive email notifications (requires confirmation)

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
