#!/usr/bin/env bash

image_name='l-25-cors-web-page'
container_name='l-25-cors-web-page'
external_port="100$((10 + RANDOM % 90))"  # from 10010 to 10099

docker build -t "$image_name" web_page/
old_docker_container_id="$(docker ps -q -f name="$container_name")"
echo "found container with same name: $old_docker_container_id"
if [ "$old_docker_container_id" != '' ]; then
  docker stop "$container_name" && docker rm "$container_name"
fi
docker run -d --name "$container_name" -p "$external_port":80 "$image_name" || echo "failed!"

echo -e "\nWEB PAGE PORT: $external_port\n"
