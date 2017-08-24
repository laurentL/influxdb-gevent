#!/usr/bin/env bash

if ! which tox; then
    echo "Please install tox using `pip install tox`"
    exit 1
fi
export PATH=/opt/pypy3.5-5.8/bin/:/opt/pypy-5.8/bin/:/opt/python3.5.4/bin/:/opt/python3.6.2/bin/:$PATH
tox $@
