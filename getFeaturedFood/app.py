import json
import os
import boto3

# getFeaturedFood
def lambda_handler(event, context):
    print('received event:')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        db_client = boto3.client('dynamodb', endpoint_url='http://docker.for.mac.localhost:8000')
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

    response = db_client.query(
        TableName=DYNAMODB_TABLE,
        IndexName='featuredIndex',
        KeyConditionExpression='featured = :featured',
        ExpressionAttributeValues={
            ':featured': {'S': 'T'},
        },
    )
    body = {"foods": response['Items']}

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body),
    }
