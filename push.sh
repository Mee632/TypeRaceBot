#!/bin/bash

# Setze die Variablen für das Image und die Registry
IMAGE_NAME="typeracebot"
IMAGE_TAG="latest"
REGISTRY_URL="registry.local.xo-6.studio"
REGISTRY_USER="synclyn"
REGISTRY_PASSWORD=""

docker build -t $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG .

echo $REGISTRY_PASSWORD | docker login $REGISTRY_URL -u $REGISTRY_USER --password-stdin

docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG

docker push $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG