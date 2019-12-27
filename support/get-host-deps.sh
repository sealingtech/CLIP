#!/bin/bash
set -e

get_os_major_version() {
	local full_version=$(rpm -q --whatprovides --queryformat '%{version}' system-release)
	echo -n ${full_version:0:1}
}

declare -a rhel_packages_yum
declare -a rhel_packages_local
declare -a rhel_packages_all

rhel_packages_common_yum=" \
 anaconda \
 dosfstools \
 e2fsprogs \
 GConf2 \
 genisoimage \
 git \
 isomd5sum \
 libcdio \
 make \
 pykickstart \
 rpm-build \
 ruby \
 squashfs-tools \
 sssd-client \
 sudo \
 syslinux \
"

rhel_packages_yum[7]=" \
 libselinux-python \
 policycoreutils-python \
 python-mako \
 system-config-keyboard \
 $rhel_packages_common_yum \
"

rhel_packages_yum[8]=" \
 policycoreutils-python-utils \
 python3-libselinux \
 python3-mako \
 xorriso \
 $rhel_packages_common_yum \
"

rhel_packages_common_local=" \
 mock
"

rhel_packages_local[7]=" \
 python-lockfile \
 $rhel_packages_common_local \
"

rhel_packages_local[8]=" \
 python2-lockfile \
 $rhel_packages_common_local \
"

rhel_packages_all[7]="${rhel_packages_yum[7]} ${rhel_packages_local[7]}"
rhel_packages_all[8]="${rhel_packages_yum[8]} ${rhel_packages_local[8]}"

usage() {
	echo "usage: $0 <all|yum>"
}

if [ $# != 1 ]; then
	usage
	exit 1
fi

major_version=$(get_os_major_version)
if [ -z "$major_version" ]; then
	echo "error: failed to determine the OS major version"
	exit 1
fi
if [ "$major_version" -ne "7" -a "$major_version" -ne "8" ]; then
	echo "error: OS version ${major_version} not supported"
	exit 1
fi

if [ $1 = "all" ]; then
	echo ${rhel_packages_all[${major_version}]}
elif [ $1 = "yum" ]; then
	echo ${rhel_packages_yum[${major_version}]}
else
	usage
	echo "error: invalid argument $1"
	exit 1
fi

