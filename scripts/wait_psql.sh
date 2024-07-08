#!/bin/sh
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for postgres database startup... ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 0.1
done

echo "🟢 Postgres database is up and running! ($POSTGRES_HOST $POSTGRES_PORT)"
