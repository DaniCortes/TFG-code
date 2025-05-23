# Despliegue de MongoDB

cd $(dirname $(readlink -f $0))

kubectl delete configmap redis-config

echo "Creando ConfigMap para inicialización de Redis..."
kubectl create configmap redis-config --from-file=./redis.conf

echo "Aplicando Volumen Persistente MongoDB..."
kubectl apply -f ./redis-pv.yaml

echo "Aplicando servicio MongoDB..."
kubectl apply -f ./redis-statefulSet.yaml
kubectl apply -f ./redis-service.yaml