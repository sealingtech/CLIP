#!/bin/bash
set -e

########
# expect script to smoke test CLIP install ISO
# by: booting ISO with qemu, installing, rebooting,
# logging in as toor, and running shutdown

DISK_IMAGE=drive.img

usage() {
  echo "usage: $0 ISO_PATH"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

if [ -e "$DISK_IMAGE" ]; then
  echo "error: disk image $DISK_IMAGE exists.  please move or remove it to continue."
  exit 1
fi

ISO_PATH="$1"

if [ ! -e "$ISO_PATH" ]; then
  usage
  echo "missing ISO_PATH $ISO_PATH"
  exit 1
fi

base_dir=$(dirname $0)

dd if=/dev/zero of=$DISK_IMAGE bs=1M count=0 seek=20000

# boot the install iso and wait for installation to complete
$base_dir/qemu-install-iso.sh $ISO_PATH $DISK_IMAGE

# qemu vm with full virt fails fips mode (fips_ecdsa_selftest) for
# some reason
if [ -z "$DISABLE_FIPS" ]; then
  if virt-host-validate | grep -q 'QEMU: Checking for hardware virtualization.*PASS'; then
    DISABLE_FIPS=n
  else
    echo "warning: disabling fips mode because hardware virtualization is not supported on this system"
    DISABLE_FIPS=y
  fi
fi
if [ "$DISABLE_FIPS" = "y" ]; then
  sudo $base_dir/disable-fips.sh $DISK_IMAGE
fi

# boot the installed vm and run login test
$base_dir/qemu-login.sh $DISK_IMAGE || true

# mount the vm image and validate SCAP results
sudo $base_dir/test-scap-results.sh $DISK_IMAGE
