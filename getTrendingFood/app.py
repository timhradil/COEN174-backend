import json
import os
import boto3
from dynamodb_json import json_util as json_db

#getTrendingFood
def lambda_handler(event, context):
    print('received event:')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        db_client = boto3.client('dynamodb', endpoint_url=os.environ['ENDPOINT_URL'])
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']

    response = db_client.query(
        TableName=DYNAMODB_TABLE,
        IndexName='trendingIndex',
        KeyConditionExpression='trending = :trending',
        ExpressionAttributeValues={
            ':trending': {'S': 'T'},
        },
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
