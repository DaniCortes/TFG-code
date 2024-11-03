# Despliegue de PostgreSQL

cd $(dirname $(readlink -f $0))


echo "Creando ConfigMap para inicialización de PostgreSQL..."
kubectl create configmap postgres-initdb-script --from-file=./init.sql

echo "Aplicando Volumen Persistente PostgreSQL..."
kubectl apply -f ./postgres-pv.yaml

echo "Aplicando servicio PostgreSQL..."
kubectl apply -f ./postgres-secret.yaml
kubectl apply -f ./postgres-statefulSet.yaml
kubectl apply -f ./postgres-service.yaml