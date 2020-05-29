#!/bin/bash

# copy files out of the root filesystem of a live iso


usage() {
  echo "usage: $0 LIVE_ISO [CP ARGS] SOURCE DEST"
}

cleanup() {
	if [ -n "$TMP_ROOT" -a -d "$TMP_ROOT" ]; then
		rm -rf "$TMP_ROOT"
	fi
}

set -e
set -x

if [ $# -lt 3 ]; then
  usage
  exit 1
fi

LIVE_ISO=$1
shift
while [ $# -gt 2 ]; do
	CP_ARGS="$CP_ARGS $1"
	shift
done
SOURCE=$1
DEST=$(realpath $2)

if [ ! -e "$LIVE_ISO" ]; then
	echo "error: iso $LIVE_ISO does not exist"
	exit 1
fi

trap cleanup EXIT

TMP_ROOT=$(mktemp -d liveiso-mount.XXXXXX)
mkdir "$TMP_ROOT/iso"
mkdir "$TMP_ROOT/squash"
mkdir "$TMP_ROOT/root"

mount_liveiso_and_cp() {
	sudo mount -o loop "$LIVE_ISO" "$TMP_ROOT/iso"
	sudo mount -o loop -t squashfs "$TMP_ROOT/iso/LiveOS/squashfs.img" "$TMP_ROOT/squash"
	sudo mount -o loop "$TMP_ROOT/squash/LiveOS/rootfs.img" "$TMP_ROOT/root"
	cd "$TMP_ROOT/root"
	cp $CP_ARGS ./$SOURCE $DEST
}
export mount_liveiso_and_cp

#sudo unshare --mount sh -c mount_liveiso_and_cp
sudo unshare --mount sh <<EOF
	sudo mount -o loop,ro "$LIVE_ISO" "$TMP_ROOT/iso"
	sudo mount -o loop -t squashfs "$TMP_ROOT/iso/LiveOS/squashfs.img" "$TMP_ROOT/squash"
	sudo mount -o loop "$TMP_ROOT/squash/LiveOS/rootfs.img" "$TMP_ROOT/root"
	cd "$TMP_ROOT/root"
	cp $CP_ARGS ./$SOURCE $DEST
EOF
#scap_result_file=$MOUNT_DIR/root/scap/post/html/results.xml
