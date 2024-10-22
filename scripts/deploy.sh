#!/bin/bash

set -e

# Despliegue de Gateway y dependencias

echo "Aplicando Gateway API CRDs..."
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.1.0/experimental-install.yaml

echo "Aplicando Contour GatewayClass..."
kubectl apply -f ./contour/gateway/gatewayclass.yaml

echo "Aplicando Contour Namespace..."
kubectl apply -f ./contour/gateway/namespace.yaml

echo "Aplicando Gateway..."
kubectl apply -f ./gateway/gateway.yaml

echo "Aplicando Contour..."
kubectl apply -f https://projectcontour.io/quickstart/contour.yaml

echo "Aplicando Contour ConfigMap..."
kubectl apply -f ./contour/gateway/configmap.yaml

echo "Reiniciando Contour..."
kubectl -n projectcontour rollout restart deployment/contour

echo "Aplicando cert-manager..."
kubectl apply -f ./cert-manager/cert-manager.yaml

echo "Aplicando cert-manager ClusterIssuer..."
kubectl apply -f ./cert-manager/cluster-issuer.yaml

echo "Esperando a que ClusterIssuer esté listo..."
kubectl wait --for=condition=Ready clusterissuer/letsencrypt-prod --timeout=300s

# Despliegue de volumen persistente y configuraciones

echo "Aplicando configuraciones..."
kubectl apply -f streams-pv.yaml
kubectl apply -f streams-pvc.yaml
kubectl apply -f ./config/configmap.yaml
kubectl apply -f ./config/secret.yaml

# Despliegue de PostgreSQL

echo "Creando ConfigMap para inicialización de PostgreSQL..."
kubectl create configmap postgres-initdb-script --from-file=./database/postgres/init.sql

echo "Aplicando Volumen Persistente PostgreSQL..."
kubectl apply -f ./database/postgres/postgres-pv.yaml

echo "Aplicando servicio PostgreSQL..."
kubectl apply -f ./database/postgres/postgres-secret.yaml
kubectl apply -f ./database/postgres/postgres-statefulSet.yaml
kubectl apply -f ./database/postgres/postgres-service.yaml

# Despliegue de MongoDB

echo "Creando ConfigMap para inicialización de PostgreSQL..."
kubectl create configmap postgres-initdb-script --from-file=./database/mongodb/init.js

echo "Aplicando Volumen Persistente MongoDB..."
kubectl apply -f ./database/mongodb/mongo-pv.yaml

echo "Aplicando servicio MongoDB..."
kubectl apply -f ./database/mongodb/mongo-statefulSet.yaml
kubectl apply -f ./database/mongodb/mongo-service.yaml

echo "Aplicando Gateway y HTTPRoute..."
kubectl apply -f ./gateway/gateway.yaml
kubectl apply -f ./gateway/httproute.yaml

echo "Aplicando servicio de registro..."
kubectl apply -f ./register-service/deployment.yaml
kubectl apply -f ./register-service/service.yaml

echo "Aplicando servicio de autenticación..."
kubectl apply -f ./auth-service/deployment.yaml
kubectl apply -f ./auth-service/service.yaml

echo "Aplicando servicio de inicio de sesión..."
kubectl apply -f ./login-service/deployment.yaml
kubectl apply -f ./login-service/service.yaml

echo "Aplicando servicio de perfil..."
kubectl apply -f ./profile-service/deployment.yaml
kubectl apply -f ./profile-service/service.yaml

echo "¡Despliegue completo!"
