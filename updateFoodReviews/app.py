import os
import json
import boto3

def getFood(review, db_client, DYNAMODB_TABLE):
   foodId = review['foodId']['S']
   response = db_client.get_item(
      TableName=DYNAMODB_TABLE,
      Key={
         'foodId':{'S': foodId}
      },
   )
   return response['Item']  

# updateFood
def lambda_handler(event, context):
   print('received event')
   print(event)

   if os.environ['ENV'] == 'local':
        db_client = boto3.client('dynamodb', endpoint_url=os.environ['ENDPOINT_URL'])
   else:
        db_client = boto3.client('dynamodb')
   DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
   
   record = event['Records'][0]
   eventName = record['eventName']

   if eventName == 'INSERT':
      review = record['dynamodb']['NewImage']
      food = getFood(review, db_client, DYNAMODB_TABLE)
      totalReviews = float(food['totalReviews']['N']) + 1
      reviewRating = float(review['rating']['N'])
      foodRating = float(food['rating']['N'])
      foodRating = (foodRating * (totalReviews - 1) + reviewRating) / totalReviews

   elif eventName == 'REMOVE':
      review = record['dynamodb']['OldImage']
      food = getFood(review, db_client, DYNAMODB_TABLE)
      totalReviews = float(food['totalReviews']['N']) - 1
      reviewRating = float(review['rating']['N'])
      foodRating = float(food['rating']['N'])
      foodRating = (foodRating * (totalReviews + 1) - reviewRating) / totalReviews
   
   elif eventName == 'MODIFY':
      new_review = record['dynamodb']['NewImage']
      old_review = record['dynamodb']['OldImage']
      food = getFood(new_review, db_client, DYNAMODB_TABLE)
      totalReviews = float(food['totalReviews']['N'])
      newReviewRating = float(new_review['rating']['N'])
      oldReviewRating = float(old_review['rating']['N'])
      foodRating = float(food['rating']['N'])
      foodRating = (foodRating * totalReviews + newReviewRating - oldReviewRating) / totalReviews

   # Update the food
   food['totalReviews'] = {'N': str(totalReviews)}
   food['rating'] = {'N': str(foodRating)}

   db_client.put_item(
      TableName=DYNAMODB_TABLE,
      Item=food,
    )



