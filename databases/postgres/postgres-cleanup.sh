#!/bin/bash

cd $(dirname $(readlink -f $0))


echo "Eliminando recursos existentes de PostgreSQL..."
kubectl delete service postgres
kubectl delete statefulset postgres
kubectl delete secret postgres-secret
kubectl delete pvc storage-postgres-0
kubectl delete pv postgres-pv
kubectl delete configmap postgres-initdb-script