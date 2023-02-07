all: deploy

build:
	sam build

test: build
	sh unitTests.sh

deploy: test
	sam deploy
