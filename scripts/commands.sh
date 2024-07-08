#!/bin/sh

# O shell ira encerrar a execucao do script quando um comando falhar
set -e

wait_psql.sh

collectstatic.sh
migrate.sh
runserver.sh