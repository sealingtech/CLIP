#!/bin/sh

MY_DIR="$( cd $( dirname "$0" ) && pwd )"

PYTHONPATH="$1" "${MY_DIR}/../tmp/tools/usr/bin/pungi" ${@:2}

