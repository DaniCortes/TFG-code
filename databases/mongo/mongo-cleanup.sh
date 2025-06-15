# Despliegue de MongoDB

cd $(dirname $(readlink -f $0))

echo "Eliminando recursos existentes de MongoDB..."

kubectl delete service mongo
kubectl delete statefulset mongo
kubectl delete secret mongo-secret
kubectl delete pvc storage-mongo-0
kubectl delete pv mongo-pv
kubectl delete configmap mongo-initdb-script