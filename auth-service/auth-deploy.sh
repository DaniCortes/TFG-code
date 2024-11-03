#!/bin/bash

cd $(dirname $(readlink -f $0))

eval $(minikube docker-env)


echo "Eliminando posible despliegue anterior"
kubectl delete -f ./deployment.yaml
kubectl delete -f ./service.yaml
kubectl delete -f ./httproute.yaml

echo "Esperando a que el despliegue se complete"
kubectl rollout status deployment/auth-service


echo "Eliminando imagen de servicio de autenticación"
sleep 2
docker rmi auth-service:latest

echo "Construyendo imagen de servicio de autenticación"
docker build -t auth-service:latest .

eval $(minikube docker-env -u)

echo "Aplicando despliegue del servicio de autenticación"
kubectl apply -f ./deployment.yaml

echo "Aplicando servicio de autenticación"
kubectl apply -f ./service.yaml

echo "Aplicando rutas de autenticación"
kubectl apply -f ./httproute.yaml