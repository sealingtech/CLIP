#!/bin/bash

# mount the vm disk image and check the scap results for failures

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
sleep 2
part_re=
is_first=1
for p in $partitions; do
  if [ $is_first = 1 ]; then
    is_first=0
    part_re="/dev/mapper/$p"
  else
    part_re="$part_re|/dev/mapper/$p"
  fi
done

mkdir $MOUNT_DIR
vg_name=$(pvs -S "pv_name=~$part_re" -o vg_name --noheadings | awk '{print $1}')
if [ -z "$vg_name" ]; then
  echo "error: failed to find logical volume group in vm disk image"
  exit 1
fi
mount /dev/$vg_name/root $MOUNT_DIR
is_mounted=1

scap_result_file=$MOUNT_DIR/root/scap/post/html/results.xml
cp -r $MOUNT_DIR/root/scap ./scap
if [ ! -e $scap_result_file ]; then
  echo "error: scap scan results do not exist"
  exit 1
else
  bad_result_re='<result>\(error\|fail\|notchecked\)'
  bad_result_count=$(grep -e "$bad_result_re" $scap_result_file | wc -l)
  if [ $bad_result_count -gt 0 ]; then
    grep -e "$bad_result_re" -B1 $scap_result_file
    echo "scap scan reported $bad_result_count failures or errors"
  fi
fi
