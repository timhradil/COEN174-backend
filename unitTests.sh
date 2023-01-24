#!/bin/sh
# Kill docker network & container for dynamoDB if running
docker rm $(docker stop $(docker ps -a -q --filter ancestor=amazon/dynamodb-local --format="{{.ID}}")) >/dev/null 2>&1
docker network rm lambda-local >/dev/null 2>&1
sleep 5

# Create docker network & container for dynamoDB
docker network create lambda-local >/dev/null 2>&1
sleep 10
docker run -p 8000:8000 --network lambda-local amazon/dynamodb-local >/dev/null 2>&1 &

# Create dynamoDB Tables
  # reviewDynamoDB Table
aws dynamodb create-table \
  --table-name reviewDynamoDB \
  --attribute-definitions AttributeName=reviewId,AttributeType=S \
                          AttributeName=userId,AttributeType=S \
                          AttributeName=foodId,AttributeType=S \
  --key-schema AttributeName=reviewId,KeyType=HASH \
  --global-secondary-indexes \
      "[ 
           {
               \"IndexName\":\"userIdIndex\",
               \"KeySchema\":[{\"AttributeName\":\"userId\",\"KeyType\":\"HASH\"}],
               \"Projection\":{\"ProjectionType\":\"INCLUDE\",\"NonKeyAttributes\":[\"rating\",\"title\",\"body\",\"dateCreated\"]},
               \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
           },
           {
               \"IndexName\":\"foodIdIndex\",
               \"KeySchema\":[{\"AttributeName\":\"foodId\",\"KeyType\":\"HASH\"}],
               \"Projection\":{\"ProjectionType\":\"INCLUDE\",\"NonKeyAttributes\":[\"rating\",\"title\",\"body\",\"dateCreated\"]},
               \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
           }
      ]" \
  --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5 \
  --endpoint-url http://localhost:8000 >/dev/null 2>&1 

  # foodDynamoDB Table
aws dynamodb create-table \
  --table-name foodDynamoDB \
  --attribute-definitions AttributeName=foodId,AttributeType=S \
                          AttributeName=featured,AttributeType=S \
                          AttributeName=trending,AttributeType=S \
                          AttributeName=current,AttributeType=S \
  --key-schema AttributeName=foodId,KeyType=HASH \
  --global-secondary-indexes \
      "[
           {
               \"IndexName\":\"featuredIndex\",
               \"KeySchema\":[{\"AttributeName\":\"featured\",\"KeyType\":\"HASH\"}],
               \"Projection\":{\"ProjectionType\":\"INCLUDE\",\"NonKeyAttributes\":[\"name\",\"rating\",\"totalReviews\",\"dateCreated\",\"tags\",\"restaurants\"]},
               \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
           },
           {
               \"IndexName\":\"trendingIndex\",
               \"KeySchema\":[{\"AttributeName\":\"trending\",\"KeyType\":\"HASH\"}],
               \"Projection\":{\"ProjectionType\":\"INCLUDE\",\"NonKeyAttributes\":[\"name\",\"rating\",\"totalReviews\",\"dateCreated\",\"tags\",\"restaurants\"]},
               \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
           },
           {
               \"IndexName\":\"currentIndex\",
               \"KeySchema\":[{\"AttributeName\":\"current\",\"KeyType\":\"HASH\"}],
               \"Projection\":{\"ProjectionType\":\"INCLUDE\",\"NonKeyAttributes\":[\"name\",\"rating\",\"totalReviews\",\"dateCreated\",\"tags\",\"restaurants\"]},
               \"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}
           }
      ]" \
  --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5 \
  --endpoint-url http://localhost:8000 >/dev/null 2>&1 

sleep 5
# Invoke lambdas locally for unit testing
  # putFood 
sam local invoke putFoodFunction -e events/putFoodEvent.json -n localFoodEnv.json --docker-network lambda-local
  # getAllFoods
sam local invoke getAllFoodFunction -e events/getAllFoodEvent.json -n localFoodEnv.json
