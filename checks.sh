#!/usr/bin/env bash

set -e

printf "\nSecurity\n\n"
pipenv check .
printf "\nStyle\n\n"
pipenv check --style .
printf "\nMypy\n\n"
pipenv run mypy aiocrypto_prices/ --ignore-missing-imports --strict-optional
printf "\nUnittests\n\n"
pipenv run python -m pytest tests --cov=aiocrypto_prices -v --durations=5
