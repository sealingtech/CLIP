#!/bin/bash

# mount the vm disk image and disable fips mode in grub conf

set -e

usage() {
  echo "usage: $0 DISK_IMG"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

DISK_IMAGE=$1

if [ ! -e "$DISK_IMAGE" ]; then
  echo "error: disk image $DISK_IMAGE does not exist"
  exit 1
fi

MOUNT_DIR=vm_root
is_mounted=0
is_partxed=0

cleanup() {
  if [ -e "$MOUNT_DIR" ]; then
    if [ "$is_mounted" = 1 ]; then
      umount $MOUNT_DIR
    fi
    rmdir $MOUNT_DIR
  fi

  if [ -n "$vg_name" ]; then
    vgchange -an $vg_name
  fi

  if [ "$is_partxed" = 1 ]; then
    kpartx -d $DISK_IMAGE
  fi
}
trap cleanup EXIT

# create block devices for partions on vm image
partitions=$(kpartx -v -s -a $DISK_IMAGE | awk '{print $3}')
is_partxed=1

# allow devmapper to settle
sleep 2

is_first=1
part_path=
part_re=
for p in $partitions; do
  if [ $is_first = 1 ]; then
    is_first=0
    part_path="/dev/mapper/$p"
    part_re="/dev/mapper/$p"
  else
    part_re="$part_re|/dev/mapper/$p"
  fi
done

vg_name=$(pvs -S "pv_name=~$part_re" -o vg_name --noheadings | awk '{print $1}')
if [ -z "$vg_name" ]; then
  echo "error: failed to find logical volume group in vm disk image"
  exit 1
fi

mkdir $MOUNT_DIR
mount $part_path $MOUNT_DIR
is_mounted=1

grub_conf_file=$MOUNT_DIR/grub2/grub.cfg
if [ ! -e $grub_conf_file ]; then
  echo "error: can't disable fips mode because grub.cfg not found"
  exit 1
else
  sed -i -e 's/fips=1/fips=0/g' $grub_conf_file
fi
