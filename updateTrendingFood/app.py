import json
import os
import boto3
import datetime
from dynamodb_json import json_util as json_db

# updateTrendingFood
def lambda_handler(event, context):
    print('received event: ')
    print(event)

    # Static Variables
    if os.environ['ENV'] == 'local':
        print(os.environ)
        db_client = boto3.client('dynamodb', endpoint_url=os.environ['ENDPOINT_URL'])
    else:
        db_client = boto3.client('dynamodb')
    DYNAMODB_FOOD_TABLE = os.environ['DYNAMODB_FOOD_TABLE']
    DYNAMODB_REVIEW_TABLE = os.environ['DYNAMODB_REVIEW_TABLE']

    body = {}
    response = db_client.scan(
        TableName=DYNAMODB_FOOD_TABLE,
    )

    foods = json_db.loads(response['Items'])
    foodIds = [food['foodId'] for food in foods]

    for foodId in foodIds:
        response = db_client.query(
            TableName=DYNAMODB_REVIEW_TABLE,
            IndexName='foodIdIndex',
            KeyConditionExpression='foodId = :foodId',
            ExpressionAttributeValues={
                ':foodId': {'S': foodId},
            },
        )
        reviews = json_db.loads(response['Items'])
        dateStrings = [review['dateCreated'] for review in reviews]
        dates = [datetime.datetime.strptime(dateString,"%m/%d/%Y, %H:%M:%S") for dateString in dateStrings]
        oneDayAgo = datetime.datetime.now() - datetime.timedelta(days=1)
        recentDates = [date for date in dates if date > oneDayAgo]
        numRecentDatesForTrending = 5
        trending = 'T' if len(recentDates) >= numRecentDatesForTrending else 'F'
        
        db_client.update_item(
            TableName=DYNAMODB_FOOD_TABLE,
            Key={
                'foodId':{'S': foodId}
            },
            UpdateExpression='SET trending = :trending',
            ExpressionAttributes={
                ':trending':{'S': trending}
            }
        )