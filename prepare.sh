#!/usr/bin/env bash

if [[ -v "${DEPLOY_ENV}" ]]; then
  pipenv install --system --deploy
  cd alembic && alembic upgrade head
else
  pipenv install
  source .env
  cd alembic && pipenv run alembic upgrade head
fi
