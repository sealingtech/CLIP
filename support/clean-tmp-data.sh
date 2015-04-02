#!/bin/bash
echo "WARNING: This script blindly removes all Pungi-related directories from /tmp."
echo "         You probably need to sudo to run this script successfully."
read -p "If anyone is building an at this time please hit ctrl-c."

pushd . 1>/dev/null
cd /tmp;
rm -rf keepfile* modinfo* instimage* keymaps* makeboot* yumcache* yumdir* buildinstall* tmp*
popd 1>/dev/null
