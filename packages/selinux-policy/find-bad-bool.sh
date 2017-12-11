#!/bin/sh
cd tmp/src/redhat/BUILD/selinux-policy
gdb -x ../../../../../gdb_badbool --args semodule_expand tmp/test.lnk policy24
