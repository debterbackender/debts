#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z ${POSTGRES_HOST} ${POSTGRES_PORT} &> /dev/null;
do
    echo "waiting for PostgreSQL to start..."
    sleep 3;
done;

echo "PostgreSQL started"

python manage.py migrate --no-input --traceback
python manage.py runserver 0.0.0.0:8000 --traceback --insecure
