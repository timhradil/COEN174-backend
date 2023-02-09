import json
import os
import boto3
from dynamodb_json import json_util as json_db

#getAllFood
def lambda_handler(event, context):
    print('received event: ')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        print(os.environ)
        db_client = boto3.client('dynamodb', endpoint_url=os.environ['ENDPOINT_URL'])
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

    body = {}
    if 'foodId' in event['body']:
        response = db_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'foodId':{'S': body['foodId']},
            },
        ) 
        body = {"food": json_db.loads(response['Item'])}
    else:        
        response = db_client.scan(
            TableName=DYNAMODB_TABLE,
        )
        body = {"foods": json_db.loads(response['Items'])}

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body),
    }
