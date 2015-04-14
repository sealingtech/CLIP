#! /bin/bash -e

shuf /usr/share/dict/words | grep -v "[^a-z][^A-Z]" | xargs -n1 2> /dev/null | awk '{ if (length($0) >=4 && length($0) <= 8) print $0 }' | head -n1
