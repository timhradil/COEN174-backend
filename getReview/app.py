import os
import json
import boto3
from dynamodb_json import json_util as json_db

# getReview
def lambda_handler(event, context):

    print('received event:')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        db_client = boto3.client('dynamodb', endpoint_url=os.environ['ENDPOINT_URL'])
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
 
    body = json.loads(event['body'])
     
    # Get review(s)
    if 'reviewId' in body:
        response = db_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'reviewId':{'S': body['reviewId']},
            },
        ) 
    elif 'userId' in body:
        response = db_client.query(
            TableName=DYNAMODB_TABLE,
            IndexName='userIdIndex',
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={
                ':userId': {'S': body['userId']},
            },
        ) 
    elif 'foodId' in body:
        response = db_client.query(
            TableName=DYNAMODB_TABLE,
            IndexName='foodIdIndex',
            KeyConditionExpression='foodId = :foodId',
            ExpressionAttributeValues={
                ':foodId': {'S': body['foodId']},
            },
        ) 

    if 'Item' in response:
        body = {"reviews": [json_db.loads(response['Item'])]}
    elif 'Items' in response:
        body = {"reviews": json_db.loads(response['Items'])}

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body),
    }
