#!/usr/bin/env bash

# Создаем кластер весом 1 Гб и с зоной default
docker exec garage /garage layout assign $(docker exec garage /garage node id | head -n1) --zone default --capacity 1Gb

# Подтверждение создания кластера
docker exec garage /garage layout apply --version 1

# Вывод информации о активных кластерах
docker exec garage /garage status

# Создаём новый бакет с именем data-bucket
docker exec garage /garage bucket create data-bucket

# Создаём новый ключ с именем data-key
docker exec garage /garage key create data-key

# Подсоединяем ключ data-key к data-bucket с правами к чтению, записи, и владению
docker exec garage /garage bucket allow data-bucket --read --write --owner --key data-key

# Получение полной информации о data-key
docker exec garage /garage key info --show-secret data-key
