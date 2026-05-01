#!/bin/sh

while true; do
  pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT

  if [ $? -eq 0 ]; then
    echo "DB is ready!"
    break
  fi

  echo "no response"
  sleep 1
done