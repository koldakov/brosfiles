#!/usr/bin/env bash

UWSGI_EXTRA=""

if [ -z "${PORT}" ]
then
  PORT=8080
fi

if [ ! -z "${BF_LOCAL_RUN}" ]
then
  UWSGI_EXTRA="--static-map /static=static"
fi

if [ -z "${BF_VENV_PATH}" ]
then
  BF_VENV_PATH=".venv"
fi

if [ ! -z "${BF_LOCAL_RUN}" ]
then
  if [ -d "$BF_VENV_PATH" ]
  then
      source $BF_VENV_PATH/bin/activate
  else
      echo "Create virtual environment with name=.venv or set existing path to BF_VENV_PATH virtual environment variable"
      exit 0
  fi
fi

python manage.py migrate

echo "Starting service on port $PORT"
echo "To change port set port to PORT virtual environment variable"
uwsgi --http :$PORT --ini configurations/server.ini $UWSGI_EXTRA
