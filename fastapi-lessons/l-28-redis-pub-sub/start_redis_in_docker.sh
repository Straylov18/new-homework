#!/usr/bin/env bash

container_name='devup-lesson-redis'

docker stop "$container_name" && docker rm "$container_name"
docker run -d --name "$container_name" \
    -p 6380:6379 \
    -e REDIS_USER_PASSWORD=master \
    redis:8 \
    "redis-server" "--requirepass" "master" || echo "failed!"

echo -e "\nGREAT SUCCESS\n"
