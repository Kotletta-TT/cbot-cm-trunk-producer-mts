#!/bin/bash
set -e

echo "pycodestyle"
pycodestyle --ignore \
  E261,W503 \
  trunk_producer_mts

echo "flake8"
flake8 --ignore \
  F401,W503 \
  trunk_producer_mts

echo "pylint"
pylint trunk_producer_mts --rcfile=./.pylintrc
