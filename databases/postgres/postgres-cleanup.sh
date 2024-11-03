#!/bin/bash

kubectl delete configmap postgres-initdb-script
#kubectl delete pv postgres-pv
kubectl delete secret postgres-secret
#kubectl delete statefulset postgres
#kubectl delete pvc storage-postgres-0
kubectl delete service postgres
