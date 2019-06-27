#!/usr/bin/env bash

pip install -U pipenv
pipenv install

# Patching /etc/hosts
sudo -- sh -c "echo '127.0.0.1 postgres.local' >> /etc/hosts"
sudo -- sh -c "echo '127.0.0.1 rabbit.local' >> /etc/hosts"

cp .env.sample .env

#echo -e "\nPYTHONPATH=$(pipenv --where)/src" >> .env
#echo -e "\nHOSTALIASES=$(pipenv --where)/.deploy/.hosts" >> .env