#!/bin/bash

# Ruta al Dockerfile
DOCKERFILE_PATH="/home/debian/elastalert/docker"

# Nombre de la imagen personalizada
IMAGE_NAME="elastalert2-custom"

# Construir la imagen personalizada
docker build -t $IMAGE_NAME $DOCKERFILE_PATH

# Desplegar el contenedor y ejecutar ElastAlert
docker run -d --name elastalert2 \
  --network tpotce_nginx_local \
  -v /home/debian/elastalert/config/config.yaml:/opt/elastalert/config.yaml \
  -v /home/debian/elastalert/rules:/opt/elastalert/rules \
  -v /home/debian/elastalert/scripts:/opt/elastalert/scripts \
  $IMAGE_NAME --verbose