#!/usr/bin/env python3
"""
Cognito User Setup Script

This script helps set up the Cognito user by handling the FORCE_CHANGE_PASSWORD status.
"""

import sys
import json
import boto3
import argparse
import subprocess


def get_terraform_outputs():
    """Get Cognito details from Terraform outputs"""
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
            'user_pool_id': outputs['cognito_user_pool_id']['value'],
            'client_id': outputs['cognito_user_pool_client_id']['value']
        }
    except Exception as e:
        print(f"Error loading Terraform outputs: {str(e)}")
        return None


def check_user_status(user_pool_id, email):
    """Check the current status of the Cognito user"""
    client = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        response = client.list_users(
            UserPoolId=user_pool_id,
            Filter=f'email = "{email}"'
        )
        
        if not response['Users']:
            print(f"✗ User {email} not found in Cognito User Pool")
            return None
        
        user = response['Users'][0]
        status = user['UserStatus']
        username = user['Username']
        
        print(f"User: {email}")
        print(f"Username: {username}")
        print(f"Status: {status}")
        
        return {'username': username, 'status': status}
        
    except Exception as e:
        print(f"Error checking user status: {str(e)}")
        return None


def set_permanent_password(user_pool_id, username, password):
    """Set a permanent password for the user (admin action)"""
    client = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        # Set permanent password
        client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=True
        )
        print(f"✓ Password set successfully for user {username}")
        return True
        
    except Exception as e:
        print(f"✗ Error setting password: {str(e)}")
        return False


def confirm_user(user_pool_id, username):
    """Confirm the user (admin action)"""
    client = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        client.admin_confirm_sign_up(
            UserPoolId=user_pool_id,
            Username=username
        )
        print(f"✓ User {username} confirmed")
        return True
        
    except Exception as e:
        # User might already be confirmed
        if 'NotAuthorizedException' in str(e) or 'already confirmed' in str(e).lower():
            print(f"ℹ User already confirmed")
            return True
        print(f"✗ Error confirming user: {str(e)}")
        return False


def test_authentication(client_id, email, password):
    """Test if authentication works"""
    client = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        if 'AuthenticationResult' in response:
            print("✓ Authentication successful!")
            return True
        else:
            print("⚠ Authentication returned unexpected response")
            return False
            
    except Exception as e:
        print(f"✗ Authentication failed: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Setup Cognito user for testing')
    parser.add_argument('--email', required=True, help='User email address')
    parser.add_argument('--password', required=True, help='Password to set')
    parser.add_argument('--user-pool-id', help='Cognito User Pool ID (optional, will read from Terraform)')
    parser.add_argument('--client-id', help='Cognito Client ID (optional, will read from Terraform)')
    
    args = parser.parse_args()
    
    # Get configuration
    if args.user_pool_id and args.client_id:
        config = {
            'user_pool_id': args.user_pool_id,
            'client_id': args.client_id
        }
    else:
        config = get_terraform_outputs()
        if not config:
            print("Failed to load configuration. Provide --user-pool-id and --client-id or ensure Terraform is deployed.")
            sys.exit(1)
    
    print("=" * 70)
    print("Cognito User Setup")
    print("=" * 70)
    print()
    
    # Check user status
    print("Step 1: Checking user status...")
    user_info = check_user_status(config['user_pool_id'], args.email)
    
    if not user_info:
        sys.exit(1)
    
    print()
    
    # Handle FORCE_CHANGE_PASSWORD status
    if user_info['status'] == 'FORCE_CHANGE_PASSWORD':
        print("Step 2: User requires password change. Setting permanent password...")
        if not set_permanent_password(config['user_pool_id'], user_info['username'], args.password):
            sys.exit(1)
        print()
    elif user_info['status'] == 'UNCONFIRMED':
        print("Step 2: User is unconfirmed. Confirming user...")
        if not confirm_user(config['user_pool_id'], user_info['username']):
            sys.exit(1)
        print()
    else:
        print(f"Step 2: User status is {user_info['status']} - no action needed")
        print()
    
    # Test authentication
    print("Step 3: Testing authentication...")
    if test_authentication(config['client_id'], args.email, args.password):
        print()
        print("=" * 70)
        print("✓ Setup complete! You can now run the test script:")
        print(f"  python3 tests/test_infrastructure.py --email {args.email} --password {args.password}")
        print("=" * 70)
        sys.exit(0)
    else:
        print()
        print("=" * 70)
        print("✗ Setup failed. Please check the error messages above.")
        print("=" * 70)
        sys.exit(1)


if __name__ == '__main__':
    main()
