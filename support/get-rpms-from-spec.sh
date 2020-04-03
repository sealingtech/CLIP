#!/bin/bash

if [ $# -ne 1 ]; then
	echo "usage: $0 SPEC_FILE"
	exit 1
fi

spec="$1"
rpmspec -q --qf '%{nvra}.rpm\n' "$spec"
