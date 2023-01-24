import os
import json
import uuid
import boto3
import datetime

# putReview
def lambda_handler(event, context):
    print('received event:')
    print(event)

    # Static Variables
    db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
   
    body = json.loads(event['body'])

    # Create item object
    if 'reviewId' in body:
        reviewId = body['reviewId']
        response = db_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'reviewId':{'S': reviewId}
            },
        )
        item = response['item']
    else:
        reviewId = str(uuid.uuid4())
        dateCreated = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        userId = body['userId']
        foodId = body['foodId']
        rating = float(body['rating'])
        item = {
            'reviewId':{'S': reviewId},
            'userId':{'S': userId},
            'foodId':{'S': foodId},
            'rating':{'N': rating},
            'dateCreated':{'S': dateCreated},
        }

    if 'title' in body:
        item['title'] = {'S': title}
    if 'body' in body:
        item['body'] = {'S': body}

    # Put object in DB
    response = db_client.put_item(
      TableName=DYNAMODB_TABLE,
      Item=item,
    )

    return {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps({}),
    }
