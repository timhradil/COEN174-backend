#!/bin/sh

VERBOSE=false
VERBOSEFILE=$(mktemp)
DEBUG=false
DEBUGFILE=$(mktemp)
ALLPASSED=true

function checkError() {
  if grep -wq "ERROR" $DEBUGFILE; then
    ALLPASSED=false
    echo "Test Failed"
    cat $DEBUG
    cat $VERBOSEFILE
    echo ""
  else
    if $DEBUG; then
      cat $DEBUGFILE
      echo ""
    fi
    if $VERBOSE; then
      cat $VERBOSEFILE
      echo ""
    fi
    echo "Test Passed"
  fi
  rm $DEBUGFILE
  DEBUGFILE=$(mktemp)
  rm $VERBOSEFILE
  VERBOSEFILE=$(mktemp)
}

while [ "$1" != "" ]; do
  case $1 in
  -v | --verbose)
    VERBOSE=true
    ;;
  -d | --debug)
    DEBUG=true
  esac
  shift
done

echo "Killing docker network & container for dynamoDB if running"
docker rm $(docker stop $(docker ps -a -q --filter ancestor=amazon/dynamodb-local --format="{{.ID}}")) >$VERBOSEFILE 2>$DEBUGFILE
docker network rm lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo "Creating docker network & container for dynamoDB"
docker network create lambda-local >$VERBOSEFILE 2>$DEBUGFILE
docker run -p 8000:8000 --network lambda-local amazon/dynamodb-local >$VERBOSEFILE 2>$DEBUGFILE &
checkError

echo "Creating dynamoDB Tables"
echo " reviewDynamoDB Table"
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
  --endpoint-url http://localhost:8000 >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " foodDynamoDB Table"
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
  --endpoint-url http://localhost:8000 >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo "Invoke lambdas locally for unit testing"
echo " putFood"
sam local invoke putFoodFunction -e events/putFoodEvent.json -n localFoodEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " getAllFoods"
sam local invoke getFoodFunction -e events/getAllFoodEvent.json -n localFoodEnv.json >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " getFood"
sam local invoke getFoodFunction -e events/getFoodEvent.json -n localFoodEnv.json >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " putReview"
sam local invoke putReviewFunction -e events/putReviewEvent.json -n localReviewEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " getReview"
sam local invoke getReviewFunction -e events/getReviewEvent.json -n localReviewEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " getReviewsByUser"
sam local invoke getReviewFunction -e events/getReviewsByUserEvent.json -n localReviewEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " getReviewsByFood"
sam local invoke getReviewFunction -e events/getReviewsByFoodEvent.json -n localReviewEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " updateTrendingReviews"
sam local invoke updateTrendingReviews -e updateTrendingFoodEvent.json -n localBothEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

echo " updateFoodReviews"
sam local invoke updateFoodReviews -e updateFoodReviewsEvent.json -n localFoodEnv.json --docker-network lambda-local >$VERBOSEFILE 2>$DEBUGFILE
checkError

if $ALLPASSED; then
  echo "All Tests Passed"
else
  raise error "A Test Failed"
fi

rm $DEBUGFILE
