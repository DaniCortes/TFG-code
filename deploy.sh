#!/bin/bash

set -e

# Despliegue de Gateway y dependencias

cd $(dirname $(readlink -f $0))


echo "Aplicando Gateway API CRDs estándar..."
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/standard-install.yaml

echo "Aplicando Gateway API CRDs experimentales..."
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.3.0/experimental-install.yaml

cd gateway

echo "Aplicando metrics-server..."
kubectl apply -f ./metrics-server.yaml

kubectl create namespace istio-system

echo "Aplicando certificado..."
kubectl apply -f ./tls-secret.yaml

echo "Aplicando Istio..."

curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.26.0 TARGET_ARCH=x86_64 sh -

cd istio-1.26.0

export PATH=$PWD/bin:$PATH
istioctl install --set values.pilot.env.PILOT_ENABLE_ALPHA_GATEWAY_API=true --set profile=minimal -y

cd ..

rm -rf istio-1.26.0

echo "Aplicando Gateway..."
kubectl apply -f ./gateway.yaml

cd ..

# Despliegue de volumen persistente y configuraciones
cd config

echo "Aplicando configuraciones..."
kubectl apply -f ./hls-pv.yaml
kubectl apply -f ./hls-pvc.yaml
kubectl apply -f ./record-pv.yaml
kubectl apply -f ./record-pvc.yaml
kubectl apply -f ./app-secrets.yaml

cd ..

# Despliegue de PostgreSQL
cd databases/postgres

echo "Creando ConfigMap para inicialización de PostgreSQL..."
kubectl create configmap postgres-initdb-script --from-file=./init.sql

echo "Aplicando Volumen Persistente PostgreSQL..."
kubectl apply -f ./postgres-pv.yaml

echo "Aplicando servicio PostgreSQL..."
kubectl apply -f ./postgres-secret.yaml
kubectl apply -f ./postgres-statefulSet.yaml
kubectl apply -f ./postgres-service.yaml

cd ..

# Despliegue de MongoDB
cd mongo

echo "Creando ConfigMap para inicialización de MongoDB..."
kubectl create configmap mongo-initdb-script --from-file=./init.js

echo "Aplicando Volumen Persistente MongoDB..."
kubectl apply -f ./mongo-pv.yaml

echo "Aplicando servicio MongoDB..."
kubectl apply -f ./mongo-secret.yaml
kubectl apply -f ./mongo-statefulSet.yaml
kubectl apply -f ./mongo-service.yaml

cd ..

# Despliegue de Redis
cd redis

echo "Creando ConfigMap para configuración de Redis..."
kubectl create configmap redis-config --from-file=./redis.conf

echo "Aplicando Volumen Persistente Redis..."
kubectl apply -f ./redis-pv.yaml

echo "Aplicando servicio Redis..."
kubectl apply -f ./redis-statefulSet.yaml
kubectl apply -f ./redis-service.yaml

cd ../..

# Despliegue de servicios

echo "Aplicando servicio de registro..."
cd user-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

cd ..

echo "Aplicando servicio de autenticación..."
cd auth-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

cd ..

echo "Aplicando servicio de información de transmisiones..."
cd stream-information-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

cd ..

echo "Aplicando servicio de ingesta..."
cd rtmp-ingest-service

kubectl create configmap rtmp-ingest-config --from-file=./nginx.conf
kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./tcproute.yaml

cd ..

echo "Aplicando servicio de transmux..."
cd transmuxing-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

cd ..

echo "Aplicando servicio de codificación..."
cd transcoding-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml

cd ..

echo "Aplicando servicio de chat..."
cd chat-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

echo "Aplicando servicio de reportes..."
cd report-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

cd ..

echo "Aplicando servicio de distribución HLS..."
cd hls-distribution-service

kubectl apply -f ./deployment.yaml
kubectl apply -f ./service.yaml
kubectl apply -f ./httproute.yaml

cd ..


echo "¡Despliegue completo!"
