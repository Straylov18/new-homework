#!/usr/bin/env bash

echo "Введите имя пользователя:"
read YOUR_USERNAME

echo "Введите пароль (ввод скрыт):"
read -s YOUR_PASSWORD
echo  # перевод строки после скрытого ввода

htpasswd -nbBC 10 "$YOUR_USERNAME" "$YOUR_PASSWORD" | sed 's/\$/$$/g'
