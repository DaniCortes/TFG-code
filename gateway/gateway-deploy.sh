#!/bin/bash

# Set the path to the gateway directory
cd $(dirname $(readlink -f $0))

kubectl delete -f ./tls-secret.yaml
kubectl delete -f ./gateway.yaml
kubectl delete -f ./metrics-server.yaml

kubectl apply -f ./tls-secret.yaml
kubectl apply -f ./metrics-server.yaml
kubectl apply -f ./gateway.yaml