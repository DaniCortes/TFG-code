#!/bin/bash

cd $(dirname $(readlink -f $0))

echo "Aplicando despliegue del servicio de login"
kubectl apply -f ./deployment.yaml

echo "Aplicando servicio de login"
kubectl apply -f ./service.yaml

echo "Aplicando rutas de login"
kubectl apply -f ./httproute.yaml