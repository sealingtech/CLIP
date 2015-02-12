#!/bin/sh
# Copyright (C) 2014, Quark Security, Inc.
#
# Aurhor: Brandon Whalen <brandon@quarksecurity.com>

# I'm sure this will be better one day
# but for now....
# just pass in the new sftp user name and it'll do the tasks to
# properly add a customer
# semanage user -a -R "staff_r" $CUSTOMER_u
# useradd -g sftp-only -Z $CUSTOMER_u $CUSTOMER
# mkdir -m 710 /home/$CUSTOMER/.ssh
# touch /home/$CUSTOMER/.ssh/authorized_keys
# chown -R :sftp-only hypori/.ssh/
# chmod 744 /home/$CUSTOMER/.ssh/authorized_keys
# chcon -R  user_u:object_r:ssh_home_t:s0 /home/$CUSTOMER/.ssh/
# PUT THE CUSTOMER KEY IN AUTHORIZED KEYS

add_user() {
        semanage user -a -R "staff_r" $1_u
        useradd -g sftp-only -Z $1_u $1
        mkdir -m 710 /home/$1/.ssh
        touch /home/$1/.ssh/authorized_keys
        chown -R :sftp-only /home/$1/.ssh/
        chmod 644 /home/$1/.ssh/authorized_keys
        chcon -R  user_u:object_r:ssh_home_t:s0 /home/$1/.ssh/
        usermod -d /$1 $1
        usermod -s /sbin/nologin $1
}

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
if [ "$#" -ne 1 ]; then
        echo "Usage: add_customer.sh [customer]"
else
        add_user $1
fi
