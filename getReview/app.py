import os
import json
import boto3

# getReview
def lambda_handler(event, context):

    print('received event:')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        db_client = boto3.client('dynamodb', endpoint_url='http://docker.for.mac.localhost:8000')
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
 
    body = json.loads(event['body'])
     
    # Get review(s)
    if 'reviewId' in body:
        response = db_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'reviewId':{'S': reviewId},
            },
        ) 
    elif 'userId' in body:
        response = db_client.query(
            TableName=DYNAMODB_TABLE,
            IndexName='userIdIndex',
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={
                ':userId': {'S': userId},
            },
        ) 
    elif 'foodId' in body:
        response = db_client.query(
            TableName=DYNAMODB_TABLE,
            IndexName='foodIdIndex',
            KeyConditionExpression='foodId = :foodId',
            ExpressionAttributeValues={
                ':foodId': {'S': foodId},
            },
        ) 

    body = {"reviews": response['Items']}

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body);
    }
