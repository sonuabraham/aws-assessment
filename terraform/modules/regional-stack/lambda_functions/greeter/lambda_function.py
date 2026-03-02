import json
import os
import uuid
from datetime import datetime
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        table_name = os.environ['DYNAMODB_TABLE']
        sns_topic_arn = os.environ['SNS_TOPIC_ARN']
        user_email = os.environ['USER_EMAIL']
        github_repo = os.environ['GITHUB_REPO']
        region = os.environ['AWS_REGION']
        
        record_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        dynamodb.put_item(
            TableName=table_name,
            Item={
                'id': {'S': record_id},
                'timestamp': {'S': timestamp},
                'region': {'S': region},
                'source': {'S': 'api'}
            }
        )
        logger.info(f"Record written to DynamoDB: {record_id}")
        
        sns_message = {
            'email': user_email,
            'source': 'Lambda',
            'region': region,
            'repo': github_repo
        }
        
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(sns_message)
        )
        logger.info(f"SNS message published to {sns_topic_arn}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Greeting processed',
                'region': region,
                'timestamp': timestamp,
                'record_id': record_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
