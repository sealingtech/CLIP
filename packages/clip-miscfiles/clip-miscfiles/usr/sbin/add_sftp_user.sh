#!/bin/bash
# Copyright (C) 2014-2015, Quark Securityyyp, Inc.
#
# Aurhor: Brandon Whalen <brandon@quarksecurity.com>
#	  Spencer Shimko <spencer@quarksecurity.com>

add_user() {
        semanage user -a -R "staff_r" $1_u
        useradd -g sftp-only -Z $1_u $1
        mkdir -m 710 /home/$1/.ssh
        touch /home/$1/.ssh/authorized_keys
        chown -R :sftp-only /home/$1/.ssh/
        chmod 644 /home/$1/.ssh/authorized_keys
        usermod -d /$1 $1
        usermod -s /sbin/nologin $1
	semanage fcontext -a -s user_u -t ssh_home_t /home/$1/.ssh
	semanage fcontext -a -s user_u -t ssh_home_t /home/$1/.ssh/authorized_keys
	restorecon -RF /home/$1/.ssh
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
        echo "Usage: $0 [customer]"
else
        add_user $1
	add_key $1
fi

