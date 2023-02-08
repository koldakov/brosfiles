#!/usr/bin/env bash

if [ -z "${PORT}" ]
then
  PORT=8080
fi

python manage.py collectstatic --noinput
python manage.py migrate

echo "Starting service on port $PORT"
echo "To change port set port to PORT virtual environment variable"
uwsgi --http :$PORT --ini configurations/server.ini --static-map /static=static --static-map /favicon.ico=favicon.ico
