import os
import json
import uuid
import boto3
import datetime

# putFood
def lambda_handler(event, context):
    print('received event:')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        print(os.environ)
        db_client = boto3.client('dynamodb', endpoint_url=os.environ['ENDPOINT_URL'])
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
    print(DYNAMODB_TABLE)
   
    body = json.loads(event['body'])

    # Create item object
    if 'foodId' in body:
        foodId = body['foodId']
        response = db_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'foodId':{'S': foodId}
            },
        )
        item = response['Item']
    else:
        if os.environ['ENV'] == 'local':
            foodId = "0"
        else:
            foodId = str(uuid.uuid4())
        dateCreated = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        item = {
            'foodId':{'S': foodId},
            'featured':{'S': 'F'},
            'trending':{'S': 'F'},
            'current':{'S': 'F'},
            'dateCreated':{'S': dateCreated},
            'rating':{'N': "0"},
            'totalReviews':{'N': "0"},
        }

    if 'featured' in body: 
        item['featured'] = {'S': body['featured']}
    if 'current' in body:
        item['current'] = {'S': body['current']}
    if 'name' in body:
        item['name'] = {'S': body['name']}
    if 'restaurants' in body:
        restaurants = [{'S' : restaurant} for restaurant in body['restaurants']]
        item['restaurants'] = {'L': restaurants}
    if 'tags' in body:
        tags = [{'S' : tag} for tag in body['tags']]
        item['tags'] = {'L': tags}

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
