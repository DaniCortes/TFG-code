#!/bin/bash

cd $(dirname $(readlink -f $0))

eval $(minikube docker-env)


echo "Eliminando posible despliegue anterior"
kubectl delete -f ./deployment.yaml
kubectl delete -f ./service.yaml
kubectl delete -f ./httproute.yaml

echo "Esperando a que el despliegue se complete"
kubectl rollout status deployment/login-service


echo "Eliminando imagen de servicio de edición de perfiles"
sleep 1.5
docker rmi login-service:latest

echo "Construyendo imagen de servicio de edición de perfiles"
docker build -t login-service:latest .

eval $(minikube docker-env -u)

echo "Aplicando despliegue del servicio de inicio de sesión"
kubectl apply -f ./deployment.yaml

echo "Aplicando servicio de inicio de sesión"
kubectl apply -f ./service.yaml

echo "Aplicando rutas de inicio de sesión"
kubectl apply -f ./httproute.yaml