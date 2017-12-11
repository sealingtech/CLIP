#!/bin/sh

MY_DIR="$( cd $( dirname "$0" ) && pwd )"

export PATH="${MY_DIR}/../tmp/tools/usr/bin:${MY_DIR}/../tmp/tools/usr/sbin:${PATH}"
PYTHONPATH="$1" "${MY_DIR}/../tmp/tools/usr/bin/livecd-creator" ${@:2}

