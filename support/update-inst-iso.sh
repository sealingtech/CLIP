#!/bin/sh
# Copyright (c) 2018 Quark Security, Inc. All rights reserved.
#Author: Marshall Miller <marshall@quarksecurity.com>
#set -x

usage() {
	echo "usage: $0 BUILDTIME_KS INSTALLTIME_KS ISO_ROOT"
	echo "This script takes kickstarts and an extracted install iso as"
	echo "inputs and modifies the install iso location by replacing"
	echo "packages and kickstart and includes based on the supplied"
	echo "kickstarts"
	echo ""
	echo "     BUILDTIME_KS     The path to the build-time variant of the"
	echo "                      kickstart (e.g., tmp/clip-minimal/clip-minimal.ks)"
	echo "     INSTALLTIME_KS   The path to the install-time variant of the"
	echo "                      kickstart (e.g., tmp/clip-minimal/a759282/x86_64/os/clip-minimal.ks)"
	echo "     ISO_ROOT         The path to the root directory of the extracted iso"
}

if [ "$#" -ne 3 ]; then
	usage
	exit 1
fi

BUILDTIME_KS="$1"
INSTALLTIME_KS="$2"
ISO_ROOT="$3"

INCLUDES=$(dirname $INSTALLTIME_KS)/includes
KICKSTART_PARSER=$(dirname "${BASH_SOURCE[0]}")/kickstart-parser.py
REPOS_DIR=$(dirname "${BASH_SOURCE[0]}")/../repos/

if [ ! -e "$BUILDTIME_KS" ]; then
	echo "error: kickstart path $BUILDTIME_KS does not exist"
	exit 1
fi

if [ ! -e "$INSTALLTIME_KS" ]; then
	echo "error: kickstart path $INSTALLTIME_KS does not exist"
	exit 1
fi

if [ ! -d "$ISO_ROOT" ]; then
	echo "error: iso root $ISO_ROOT does not exist"
	exit 1
fi

if [ ! -e "$INCLUDES" ]; then
	echo "error: did not find kickstart includes directory at $INCLUDES"
	exit 1
fi

# copy all packages
rm -rf "$ISO_ROOT"/Packages/*
$KICKSTART_PARSER "$BUILDTIME_KS" -o expected-packages || exit 1
grep -v -e '^#' expected-packages | while read p; do
	find $REPOS_DIR -name $p.rpm -exec cp '{}' "$ISO_ROOT"/Packages/ \;
done
rm expected-packages

# copy kickstart and includes
cp "$INSTALLTIME_KS" "$ISO_ROOT"/
cp "$INCLUDES"/* "$ISO_ROOT"/includes/

# update the yum repo
cd "$ISO_ROOT"
rm -rf .olddata
# TODO: generate a new comps file rather than reusing the existing one
COMPS_FILE=$(find repodata -name '*comps*.xml')
createrepo -g $COMPS_FILE .
