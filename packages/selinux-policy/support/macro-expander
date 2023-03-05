#!/bin/bash

function usage {
    echo "Usage: $0 [ -c | -t [ -M ] ] <macro>"
    echo "Options:
  -c     generate CIL output
  -t     generate standard policy source format (.te) allow rules - this is default
  -M     generate complete module .te output
"
}

function cleanup {
    rm -rf $TEMP_STORE
}

while getopts "chMt" opt; do
    case $opt in
        c) GENCIL=1
           ;;
        t) GENTE=1
           ;;
        M) GENTEMODULE=1
           ;;
        h) usage
           exit 0
           ;;
        \?) usage
           exit 1
           ;;
    esac
done

shift $((OPTIND-1))

SELINUX_MACRO=$1

if [ -z "$SELINUX_MACRO" ]
then
    exit 1
fi

TEMP_STORE="$(mktemp -d)"
cd $TEMP_STORE || exit 1

IFS="("
set $1
SELINUX_DOMAIN="${2::-1}"

echo -e "policy_module(expander, 1.0.0) \n" \
     "gen_require(\`\n" \
     "type $SELINUX_DOMAIN ; \n" \
     "')" > expander.te

echo "$SELINUX_MACRO" >> expander.te

make -f /usr/share/selinux/devel/Makefile tmp/all_interfaces.conf &> /dev/null

if [ "x$GENCIL" = "x1" ]; then

    make -f /usr/share/selinux/devel/Makefile expander.pp &> /dev/null
    MAKE_RESULT=$?

    if [ $MAKE_RESULT -ne 2 ]
    then
        /usr/libexec/selinux/hll/pp < $TEMP_STORE/expander.pp > $TEMP_STORE/expander.cil 2> /dev/null
        grep -v "cil_gen_require" $TEMP_STORE/expander.cil | sort -u
    fi
fi

if [ "$GENTE" = "1" ] || [ "x$GENCIL" != "x1" ]; then
    m4 -D enable_mcs -D distro_redhat -D hide_broken_symptoms -D mls_num_sens=16 -D mls_num_cats=1024 -D mcs_num_cats=1024 -s /usr/share/selinux/devel/include/support/file_patterns.spt /usr/share/selinux/devel/include/support/ipc_patterns.spt /usr/share/selinux/devel/include/support/obj_perm_sets.spt /usr/share/selinux/devel/include/support/misc_patterns.spt /usr/share/selinux/devel/include/support/misc_macros.spt /usr/share/selinux/devel/include/support/all_perms.spt /usr/share/selinux/devel/include/support/mls_mcs_macros.spt /usr/share/selinux/devel/include/support/loadable_module.spt tmp/all_interfaces.conf expander.te > expander.tmp 2> /dev/null
    if [ "x$GENTEMODULE" = "x1" ]; then
       #    sed '/^#.*$/d;/^\s*$/d;/^\s*class .*/d;/^\s*category .*/d;s/^\s*//' expander.tmp
        sed '/^#.*$/d;/^\s*$/d;/^\s*category .*/d;s/^\s*//' expander.tmp
    else
        grep  '^\s*allow' expander.tmp | sed 's/^\s*//'
    fi
fi

cd - > /dev/null || exit 1
cleanup
