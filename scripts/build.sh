#!/bin/bash

eval $(minikube docker-env)

cd $(dirname $(readlink -f $0))

# Build Docker images for each service
cd ..

echo "Creando imagenes de servicio de autenticación..."
cd auth-service
docker build -t auth-service:latest .

cd ..

echo "Creando imagenes de servicio de chat..."
cd chat-service
docker build -t chat-service:latest .

cd ..

echo "Creando imagenes de servicio de distribución HLS..."
cd hls-distribution-service
docker build -t hls-distribution-service:latest .

cd ..

echo "Creando imagenes de servicio de inicio de sesión..."
cd login-service
docker build -t login-service:latest .

cd ..

echo "Creando imagenes de servicio de perfil..."
cd profile-service
docker build -t profile-service:latest .

cd ..

echo "Creando imagenes de servicio de registro..."
cd register-service
docker build -t register-service:latest .

cd ..

echo "Creando imagenes de servicio de reportes..."
cd report-service
docker build -t report-service:latest .

cd ..

echo "Creando imagenes de servicio de información de retransmisiones..."
cd stream-information-service
docker build -t stream-information-service:latest .

cd ..

echo "Creando imagenes de servicio de codificación..."
cd transcoding-service
docker build -t transcoding-service:latest .

cd ..

echo "Creando imagenes de servicio de transmux..."
cd transmuxing-service
docker build -t transmuxing-service:latest .


eval $(minikube docker-env -u)

