#!/usr/bin/env python3
"""
Multi-Region Infrastructure Test Script

Tests the deployed AWS infrastructure by:
1. Authenticating with Cognito
2. Concurrently testing API endpoints in both regions
3. Validating responses and measuring latency
"""

import json
import sys
import time
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, Optional

import boto3
import requests


def authenticate_cognito(user_pool_id: str, client_id: str, username: str, password: str) -> Optional[str]:
    """
    Authenticate with Cognito and retrieve JWT IdToken.
    
    Args:
        user_pool_id: Cognito User Pool ID
        client_id: Cognito User Pool Client ID
        username: User email address
        password: User password
        
    Returns:
        IdToken string if successful, None otherwise
    """
    try:
        cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        id_token = response['AuthenticationResult']['IdToken']
        return id_token
        
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return None



def call_greet_endpoint(endpoint: str, id_token: str, region: str) -> Tuple[bool, Dict, float]:
    """
    Call the /greet endpoint and measure latency.
    
    Args:
        endpoint: API Gateway endpoint URL
        id_token: JWT token for authorization
        region: Region name for validation
        
    Returns:
        Tuple of (success, response_data, latency_seconds)
    """
    start_time = time.time()
    
    try:
        headers = {'Authorization': id_token}
        url = f"{endpoint.rstrip('/')}/greet"
        
        response = requests.post(url, headers=headers, timeout=30)
        latency = time.time() - start_time
        
        if response.status_code == 200:
            return True, response.json(), latency
        else:
            return False, {'error': response.text, 'status_code': response.status_code}, latency
            
    except Exception as e:
        latency = time.time() - start_time
        return False, {'error': str(e)}, latency


def call_dispatch_endpoint(endpoint: str, id_token: str, region: str) -> Tuple[bool, Dict, float]:
    """
    Call the /dispatch endpoint and measure latency.
    
    Args:
        endpoint: API Gateway endpoint URL
        id_token: JWT token for authorization
        region: Region name for validation
        
    Returns:
        Tuple of (success, response_data, latency_seconds)
    """
    start_time = time.time()
    
    try:
        headers = {'Authorization': id_token}
        url = f"{endpoint.rstrip('/')}/dispatch"
        
        response = requests.post(url, headers=headers, timeout=30)
        latency = time.time() - start_time
        
        if response.status_code == 200:
            return True, response.json(), latency
        else:
            return False, {'error': response.text, 'status_code': response.status_code}, latency
            
    except Exception as e:
        latency = time.time() - start_time
        return False, {'error': str(e)}, latency


def test_endpoints_concurrently(id_token: str, api_endpoint_us: str, api_endpoint_eu: str) -> Dict:
    """
    Test both regional endpoints concurrently.
    
    Args:
        id_token: JWT token for authorization
        api_endpoint_us: US-EAST-1 API endpoint
        api_endpoint_eu: EU-WEST-1 API endpoint
        
    Returns:
        Dictionary containing test results for both regions
    """
    results = {}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        futures = {
            executor.submit(call_greet_endpoint, api_endpoint_us, id_token, 'us-east-1'): ('us-east-1', 'greet'),
            executor.submit(call_greet_endpoint, api_endpoint_eu, id_token, 'eu-west-1'): ('eu-west-1', 'greet'),
            executor.submit(call_dispatch_endpoint, api_endpoint_us, id_token, 'us-east-1'): ('us-east-1', 'dispatch'),
            executor.submit(call_dispatch_endpoint, api_endpoint_eu, id_token, 'eu-west-1'): ('eu-west-1', 'dispatch'),
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            region, endpoint_type = futures[future]
            success, data, latency = future.result()
            
            if region not in results:
                results[region] = {}
            
            results[region][endpoint_type] = {
                'success': success,
                'data': data,
                'latency': latency
            }
    
    return results



def validate_and_print_results(results: Dict) -> bool:
    """
    Validate test results and print formatted output.
    
    Args:
        results: Dictionary containing test results from both regions
        
    Returns:
        True if all tests passed, False otherwise
    """
    print("\n" + "=" * 80)
    print("MULTI-REGION INFRASTRUCTURE TEST RESULTS")
    print("=" * 80)
    
    all_passed = True
    
    for region in ['us-east-1', 'eu-west-1']:
        if region not in results:
            print(f"\n✗ {region.upper()}: No results available")
            all_passed = False
            continue
        
        print(f"\n{region.upper()} Region:")
        print("-" * 80)
        
        # Test /greet endpoint
        if 'greet' in results[region]:
            greet_result = results[region]['greet']
            
            if greet_result['success']:
                data = greet_result['data']
                latency_ms = greet_result['latency'] * 1000
                
                # Validate HTTP 200 (already validated by success flag)
                # Validate region field matches expected region
                response_region = data.get('region', '')
                region_match = response_region == region
                
                if region_match:
                    print(f"  ✓ /greet endpoint: SUCCESS")
                    print(f"    - Status: 200 OK")
                    print(f"    - Region: {response_region} (matches expected)")
                    print(f"    - Latency: {latency_ms:.2f} ms")
                    print(f"    - Response: {json.dumps(data, indent=6)}")
                else:
                    print(f"  ✗ /greet endpoint: FAILED")
                    print(f"    - Region mismatch: expected {region}, got {response_region}")
                    all_passed = False
            else:
                print(f"  ✗ /greet endpoint: FAILED")
                error_data = greet_result['data']
                if 'status_code' in error_data:
                    print(f"    - Status: {error_data['status_code']}")
                print(f"    - Error: {error_data.get('error', 'Unknown error')}")
                all_passed = False
        
        # Test /dispatch endpoint
        if 'dispatch' in results[region]:
            dispatch_result = results[region]['dispatch']
            
            if dispatch_result['success']:
                data = dispatch_result['data']
                latency_ms = dispatch_result['latency'] * 1000
                
                # Validate region field if present
                response_region = data.get('region', '')
                region_match = response_region == region if response_region else True
                
                if region_match:
                    print(f"  ✓ /dispatch endpoint: SUCCESS")
                    print(f"    - Status: 200 OK")
                    if response_region:
                        print(f"    - Region: {response_region} (matches expected)")
                    print(f"    - Latency: {latency_ms:.2f} ms")
                    print(f"    - Response: {json.dumps(data, indent=6)}")
                else:
                    print(f"  ✗ /dispatch endpoint: FAILED")
                    print(f"    - Region mismatch: expected {region}, got {response_region}")
                    all_passed = False
            else:
                print(f"  ✗ /dispatch endpoint: FAILED")
                error_data = dispatch_result['data']
                if 'status_code' in error_data:
                    print(f"    - Status: {error_data['status_code']}")
                print(f"    - Error: {error_data.get('error', 'Unknown error')}")
                all_passed = False
    
    # Print latency comparison
    print("\n" + "=" * 80)
    print("LATENCY COMPARISON")
    print("=" * 80)
    
    for region in ['us-east-1', 'eu-west-1']:
        if region in results:
            print(f"\n{region.upper()}:")
            if 'greet' in results[region]:
                latency_ms = results[region]['greet']['latency'] * 1000
                print(f"  /greet:    {latency_ms:7.2f} ms")
            if 'dispatch' in results[region]:
                latency_ms = results[region]['dispatch']['latency'] * 1000
                print(f"  /dispatch: {latency_ms:7.2f} ms")
    
    # Print summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 80 + "\n")
    
    return all_passed



def load_terraform_outputs() -> Optional[Dict]:
    """
    Load configuration from Terraform outputs.
    
    Returns:
        Dictionary with configuration values or None if failed
    """
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
        }
    except Exception as e:
        print(f"Warning: Could not load Terraform outputs: {str(e)}")
        return None


def load_config_file(config_file: str) -> Optional[Dict]:
    """
    Load configuration from JSON file.
    
    Args:
        config_file: Path to JSON configuration file
        
    Returns:
        Dictionary with configuration values or None if failed
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return None


def get_config_from_env() -> Dict:
    """
    Get configuration from environment variables.
    
    Returns:
        Dictionary with configuration values from environment
    """
    return {
        'cognito_user_pool_id': os.environ.get('COGNITO_USER_POOL_ID'),
        'cognito_client_id': os.environ.get('COGNITO_CLIENT_ID'),
        'api_endpoint_us': os.environ.get('API_ENDPOINT_US'),
        'api_endpoint_eu': os.environ.get('API_ENDPOINT_EU'),
        'username': os.environ.get('COGNITO_USERNAME'),
        'password': os.environ.get('COGNITO_PASSWORD'),
    }


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(
        description='Test multi-region AWS infrastructure deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using command-line arguments
  python3 test_deployment.py \\
    --username user@example.com \\
    --password MyPassword123! \\
    --user-pool-id us-east-1_xxxxx \\
    --client-id xxxxxxxxxx \\
    --api-endpoint-us https://xxx.execute-api.us-east-1.amazonaws.com \\
    --api-endpoint-eu https://xxx.execute-api.eu-west-1.amazonaws.com

  # Using environment variables
  export COGNITO_USERNAME=user@example.com
  export COGNITO_PASSWORD=MyPassword123!
  export COGNITO_USER_POOL_ID=us-east-1_xxxxx
  export COGNITO_CLIENT_ID=xxxxxxxxxx
  export API_ENDPOINT_US=https://xxx.execute-api.us-east-1.amazonaws.com
  export API_ENDPOINT_EU=https://xxx.execute-api.eu-west-1.amazonaws.com
  python3 test_deployment.py

  # Using config file
  python3 test_deployment.py --config-file config.json

  # Auto-load from Terraform outputs
  python3 test_deployment.py --username user@example.com --password MyPassword123!
        """
    )
    
    parser.add_argument('--username', help='Cognito username (email)')
    parser.add_argument('--password', help='Cognito password')
    parser.add_argument('--user-pool-id', help='Cognito User Pool ID')
    parser.add_argument('--client-id', help='Cognito User Pool Client ID')
    parser.add_argument('--api-endpoint-us', help='US-EAST-1 API Gateway endpoint')
    parser.add_argument('--api-endpoint-eu', help='EU-WEST-1 API Gateway endpoint')
    parser.add_argument('--config-file', help='JSON configuration file')
    
    args = parser.parse_args()
    
    # Load configuration from multiple sources (priority: args > config file > env > terraform)
    config = {}
    
    # Try Terraform outputs first
    terraform_config = load_terraform_outputs()
    if terraform_config:
        config.update(terraform_config)
    
    # Try environment variables
    env_config = get_config_from_env()
    config.update({k: v for k, v in env_config.items() if v is not None})
    
    # Try config file
    if args.config_file:
        file_config = load_config_file(args.config_file)
        if file_config:
            config.update(file_config)
    
    # Override with command-line arguments
    if args.username:
        config['username'] = args.username
    if args.password:
        config['password'] = args.password
    if args.user_pool_id:
        config['cognito_user_pool_id'] = args.user_pool_id
    if args.client_id:
        config['cognito_client_id'] = args.client_id
    if args.api_endpoint_us:
        config['api_endpoint_us'] = args.api_endpoint_us
    if args.api_endpoint_eu:
        config['api_endpoint_eu'] = args.api_endpoint_eu
    
    # Validate required configuration
    required_fields = [
        'username', 'password', 'cognito_user_pool_id', 
        'cognito_client_id', 'api_endpoint_us', 'api_endpoint_eu'
    ]
    
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print("Error: Missing required configuration:")
        for field in missing_fields:
            print(f"  - {field}")
        print("\nProvide configuration via:")
        print("  - Command-line arguments (--username, --password, etc.)")
        print("  - Environment variables (COGNITO_USERNAME, COGNITO_PASSWORD, etc.)")
        print("  - Config file (--config-file config.json)")
        print("  - Terraform outputs (automatic if terraform/ directory exists)")
        sys.exit(1)
    
    print("=" * 80)
    print("MULTI-REGION INFRASTRUCTURE TEST")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  User Pool ID: {config['cognito_user_pool_id']}")
    print(f"  Client ID: {config['cognito_client_id']}")
    print(f"  Username: {config['username']}")
    print(f"  US Endpoint: {config['api_endpoint_us']}")
    print(f"  EU Endpoint: {config['api_endpoint_eu']}")
    
    # Step 1: Authenticate
    print("\n" + "=" * 80)
    print("STEP 1: AUTHENTICATING WITH COGNITO")
    print("=" * 80)
    
    id_token = authenticate_cognito(
        config['cognito_user_pool_id'],
        config['cognito_client_id'],
        config['username'],
        config['password']
    )
    
    if not id_token:
        print("\n✗ Authentication failed. Cannot proceed with tests.")
        sys.exit(1)
    
    print("✓ Authentication successful")
    
    # Step 2: Test endpoints concurrently
    print("\n" + "=" * 80)
    print("STEP 2: TESTING API ENDPOINTS CONCURRENTLY")
    print("=" * 80)
    print("\nCalling /greet and /dispatch endpoints in both regions...")
    
    results = test_endpoints_concurrently(
        id_token,
        config['api_endpoint_us'],
        config['api_endpoint_eu']
    )
    
    # Step 3: Validate and print results
    all_passed = validate_and_print_results(results)
    
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
