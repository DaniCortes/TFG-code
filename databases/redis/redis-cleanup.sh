#!/bin/bash

cd $(dirname $(readlink -f $0))


echo "Eliminando recursos existentes de Redis..."
kubectl delete service redis
kubectl delete statefulset redis
kubectl delete pvc snapshots-redis-0
kubectl delete pv redis-pv
kubectl delete configmap redis-config