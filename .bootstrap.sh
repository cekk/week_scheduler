#!/bin/bash
# we want to exit on errors
set -e

VIRTUALENV_BIN=`which virtualenv || which virtualenv-3.6`
PYTHON=`which python3 || which python`
"$VIRTUALENV_BIN" -p "$PYTHON" .

# Let's enter the virtualenv
. bin/activate
./bin/pip install -r requirements.txt
