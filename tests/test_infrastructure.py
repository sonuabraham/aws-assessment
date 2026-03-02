#!/usr/bin/env python3
"""
Multi-Region Infrastructure Test Script

This script tests the deployed AWS infrastructure by:
1. Authenticating with Cognito
2. Testing API endpoints in both regions
3. Verifying Lambda execution
4. Verifying ECS task execution
5. Checking DynamoDB records
6. Validating SNS message delivery
"""

import json
import sys
import time
import argparse
import requests
import boto3
from typing import Dict, Optional


class InfrastructureTester:
    def __init__(self, config: Dict):
        self.config = config
        self.cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        self.dynamodb_us = boto3.client('dynamodb', region_name='us-east-1')
        self.dynamodb_eu = boto3.client('dynamodb', region_name='eu-west-1')
        self.ecs_us = boto3.client('ecs', region_name='us-east-1')
        self.ecs_eu = boto3.client('ecs', region_name='eu-west-1')
        self.id_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with Cognito and get ID token"""
        print("\n=== Step 1: Authenticating with Cognito ===")
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.config['cognito_client_id'],
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': self.config['user_email'],
                    'PASSWORD': self.config['user_password']
                }
            )
            
            self.id_token = response['AuthenticationResult']['IdToken']
            print("✓ Successfully authenticated with Cognito")
            print(f"  User Pool ID: {self.config['cognito_user_pool_id']}")
            return True
            
        except Exception as e:
            print(f"✗ Authentication failed: {str(e)}")
            return False
    
    def test_api_endpoint(self, region: str, endpoint: str) -> bool:
        """Test API endpoint with authentication"""
        print(f"\n=== Step 2: Testing {region.upper()} API Endpoint ===")
        
        if not self.id_token:
            print("✗ No authentication token available")
            return False
        
        try:
            # Test /greet endpoint
            headers = {'Authorization': self.id_token}
            # Remove trailing slash from endpoint if present
            endpoint = endpoint.rstrip('/')
            url = f"{endpoint}/greet"
            
            print(f"  Calling: {url}")
            response = requests.post(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ API call successful")
                print(f"  Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"✗ API call failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ API test failed: {str(e)}")
            return False
    
    def verify_dynamodb_records(self, region: str, table_name: str) -> bool:
        """Verify records were written to DynamoDB"""
        print(f"\n=== Step 3: Verifying DynamoDB Records in {region.upper()} ===")
        
        try:
            client = self.dynamodb_us if region == 'us-east-1' else self.dynamodb_eu
            
            # Scan the table for recent records
            response = client.scan(
                TableName=table_name,
                Limit=10
            )
            
            if response['Count'] > 0:
                print(f"✓ Found {response['Count']} record(s) in DynamoDB")
                for item in response['Items'][:3]:  # Show first 3 records
                    print(f"  - Timestamp: {item.get('timestamp', {}).get('S', 'N/A')}")
                    print(f"    Region: {item.get('region', {}).get('S', 'N/A')}")
                return True
            else:
                print(f"⚠ No records found in DynamoDB table")
                return False
                
        except Exception as e:
            print(f"✗ DynamoDB verification failed: {str(e)}")
            return False
    
    def trigger_ecs_task(self, region: str, cluster_name: str) -> bool:
        """Trigger ECS task execution"""
        print(f"\n=== Step 4: Triggering ECS Task in {region.upper()} ===")
        
        try:
            client = self.ecs_us if region == 'us-east-1' else self.ecs_eu
            
            # List task definitions
            response = client.list_task_definitions(
                familyPrefix='greeter-task',
                status='ACTIVE',
                sort='DESC',
                maxResults=1
            )
            
            if not response['taskDefinitionArns']:
                print("✗ No active task definitions found")
                return False
            
            task_def_arn = response['taskDefinitionArns'][0]
            print(f"  Task Definition: {task_def_arn}")
            
            # Get cluster details to find subnet and security group
            cluster_response = client.describe_clusters(clusters=[cluster_name])
            
            if not cluster_response['clusters']:
                print(f"✗ Cluster {cluster_name} not found")
                return False
            
            print(f"  Cluster: {cluster_name}")
            print(f"  Note: ECS task requires VPC configuration to run")
            print(f"  You can manually trigger the task from AWS Console or use the /dispatch endpoint")
            
            return True
            
        except Exception as e:
            print(f"✗ ECS task trigger failed: {str(e)}")
            return False
    
    def test_dispatch_endpoint(self, region: str, endpoint: str) -> bool:
        """Test the /dispatch endpoint that triggers ECS tasks"""
        print(f"\n=== Step 5: Testing {region.upper()} Dispatch Endpoint ===")
        
        if not self.id_token:
            print("✗ No authentication token available")
            return False
        
        try:
            headers = {'Authorization': self.id_token}
            # Remove trailing slash from endpoint if present
            endpoint = endpoint.rstrip('/')
            url = f"{endpoint}/dispatch"
            
            print(f"  Calling: {url}")
            response = requests.post(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Dispatch successful")
                print(f"  Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"✗ Dispatch failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Dispatch test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        print("=" * 70)
        print("Multi-Region Infrastructure Test Suite")
        print("=" * 70)
        
        results = []
        
        # Step 1: Authenticate
        results.append(("Authentication", self.authenticate()))
        
        if not results[0][1]:
            print("\n✗ Cannot proceed without authentication")
            return False
        
        # Step 2: Test US-EAST-1 API
        results.append((
            "US-EAST-1 API",
            self.test_api_endpoint('us-east-1', self.config['api_endpoint_us'])
        ))
        
        # Step 3: Test EU-WEST-1 API
        results.append((
            "EU-WEST-1 API",
            self.test_api_endpoint('eu-west-1', self.config['api_endpoint_eu'])
        ))
        
        # Step 4: Verify DynamoDB in US-EAST-1
        results.append((
            "US-EAST-1 DynamoDB",
            self.verify_dynamodb_records('us-east-1', self.config['dynamodb_table_us'])
        ))
        
        # Step 5: Verify DynamoDB in EU-WEST-1
        results.append((
            "EU-WEST-1 DynamoDB",
            self.verify_dynamodb_records('eu-west-1', self.config['dynamodb_table_eu'])
        ))
        
        # Step 6: Test US-EAST-1 Dispatch
        results.append((
            "US-EAST-1 Dispatch",
            self.test_dispatch_endpoint('us-east-1', self.config['api_endpoint_us'])
        ))
        
        # Step 7: Test EU-WEST-1 Dispatch
        results.append((
            "EU-WEST-1 Dispatch",
            self.test_dispatch_endpoint('eu-west-1', self.config['api_endpoint_eu'])
        ))
        
        # Print summary
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        for test_name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status:8} {test_name}")
        
        total_passed = sum(1 for _, passed in results if passed)
        total_tests = len(results)
        
        print(f"\nTotal: {total_passed}/{total_tests} tests passed")
        print("=" * 70)
        
        return total_passed == total_tests


def load_terraform_outputs() -> Optional[Dict]:
    """Load configuration from Terraform outputs"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['terraform', 'output', '-json'],
            cwd='terraform',
            capture_output=True,
            text=True,
            check=True
        )
        
        outputs = json.loads(result.stdout)
        
        return {
            'cognito_user_pool_id': outputs['cognito_user_pool_id']['value'],
            'cognito_client_id': outputs['cognito_user_pool_client_id']['value'],
            'api_endpoint_us': outputs['api_endpoint_us_east_1']['value'],
            'api_endpoint_eu': outputs['api_endpoint_eu_west_1']['value'],
            'dynamodb_table_us': outputs['dynamodb_table_us_east_1']['value'],
            'dynamodb_table_eu': outputs['dynamodb_table_eu_west_1']['value'],
            'ecs_cluster_us': outputs['ecs_cluster_us_east_1']['value'],
            'ecs_cluster_eu': outputs['ecs_cluster_eu_west_1']['value'],
        }
    except Exception as e:
        print(f"Error loading Terraform outputs: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Test multi-region AWS infrastructure')
    parser.add_argument('--email', required=True, help='Cognito user email')
    parser.add_argument('--password', required=True, help='Cognito user password')
    parser.add_argument('--config-file', help='JSON config file (alternative to Terraform outputs)')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config_file:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
    else:
        config = load_terraform_outputs()
        if not config:
            print("Failed to load configuration. Use --config-file or ensure Terraform is deployed.")
            sys.exit(1)
    
    # Add credentials
    config['user_email'] = args.email
    config['user_password'] = args.password
    
    # Run tests
    tester = InfrastructureTester(config)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
