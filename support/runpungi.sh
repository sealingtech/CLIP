#!/bin/sh

MY_DIR="$( cd $( dirname "$0" ) && pwd )"
TOOL_PATH="${MY_DIR}/../tmp/tools/usr/bin":"${MY_DIR}/../tmp/tools/usr/sbin"

PATH=${PATH}:${TOOL_PATH} PYTHONPATH="$1" "${MY_DIR}/../tmp/tools/usr/bin/pungi" ${@:2}

