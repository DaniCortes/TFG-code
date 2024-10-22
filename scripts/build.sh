#!/bin/bash

# Build Docker images for each service
docker build -t register-service:latest ./register-service
docker build -t login-service:latest ./login-service
docker build -t auth-service:latest ./auth-service
docker build -t profile-service:latest ./profile-service
docker build -t rtmp-ingest-service:latest ./rtmp-ingest-service
docker build -t transmux-service:latest ./transmux-service
docker build -t stream-info-service:latest ./stream-info-service
docker build -t transcoding-service:latest ./transcoding-service

