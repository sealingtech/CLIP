#!/bin/bash
# Copyright (C) 2014-2015, Quark Security, Inc.
#
# Author: Brandon Whalen <brandon@quarksecurity.com>
#	  Spencer Shimko <spencer@quarksecurity.com>
set -e
add_user() {
	# address case where the username already exists 
	if semanage user -l| awk '{ print $1; }'|grep -q $1_u; then
		rand=`date|md5sum|head -c 8`
		semanage user -a -R "user_r" ${1}${rand}_u
	        useradd -g sftp-only -Z ${1}${rand}_u $1
	else 
		semanage user -a -R "user_r" $1_u
	        useradd -g sftp-only -Z $1_u $1
	fi

        mkdir -m 710 /home/$1/.ssh
        touch /home/$1/.ssh/authorized_keys
        chown -R :sftp-only /home/$1/.ssh/
        chmod 644 /home/$1/.ssh/authorized_keys
        usermod -d /$1 $1
        usermod -s /sbin/nologin $1
	semanage fcontext -a -s user_u -t ssh_home_t /home/$1/.ssh
	semanage fcontext -a -s user_u -t ssh_home_t /home/$1/.ssh/authorized_keys
	restorecon -RF /home/$1
}

add_key() {
	echo "Enter a public key for this user."
	echo "You may quit or add more keys by pressing enter with a blank line."
	while read -r key; do
		[ -z "$key" ] && break
		echo "$key" >> /home/$1/.ssh/authorized_keys""
	done
	read -r -p "Would you like to add another key (y/n)? " yes
	[[ $yes == "y" ]] && add_key $1
	restorecon -RF /home/$1/.ssh
}

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
if [ "$#" -ne 1 ]; then
        echo "Usage: $0 username"
else
	if ! id -u $1 2>/dev/null >/dev/null; then
	        add_user $1
		add_key $1
	else 
		echo "Error: Linux user already exists!"
		exit 1
	fi
fi

