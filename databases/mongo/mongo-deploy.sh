#!/bin/bash

cd $(dirname $(readlink -f $0))


echo "Creando ConfigMap para inicialización de MongoDB..."
kubectl create configmap mongo-initdb-script --from-file=./init.js

echo "Aplicando Volumen Persistente MongoDB..."
kubectl apply -f ./mongo-pv.yaml

echo "Aplicando servicio MongoDB..."
kubectl apply -f ./mongo-secret.yaml
kubectl apply -f ./mongo-statefulSet.yaml
kubectl apply -f ./mongo-service.yaml