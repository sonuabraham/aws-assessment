import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ecs = boto3.client('ecs')

def lambda_handler(event, context):
    try:
        cluster = os.environ['ECS_CLUSTER']
        task_definition = os.environ['TASK_DEFINITION']
        subnet_ids = os.environ['SUBNET_IDS'].split(',')
        security_group = os.environ['SECURITY_GROUP']
        
        response = ecs.run_task(
            cluster=cluster,
            taskDefinition=task_definition,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': [security_group],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        
        if response['tasks']:
            task = response['tasks'][0]
            task_arn = task['taskArn']
            logger.info(f"ECS task started: {task_arn}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Task dispatched',
                    'region': os.environ['AWS_REGION'],
                    'task_arn': task_arn,
                    'status': 'PENDING'
                })
            }
        else:
            logger.error("No tasks were started")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Failed to start task',
                    'message': 'No tasks were started'
                })
            }
            
    except Exception as e:
        logger.error(f"Error dispatching task: {str(e)}")
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
