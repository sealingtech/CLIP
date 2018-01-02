#!/bin/bash

########
# expect script to smoke test CLIP install ISO
# by: booting ISO with qemu, installing, rebooting


usage() {
  echo "usage: $0 ISO_PATH DISK_IMG"
}

if [ $# -ne 2 ]; then
  usage
  exit 1
fi

ISO_PATH="$1"
DISK_IMAGE="$2"

if [ ! -e "$ISO_PATH" ]; then
  usage
  echo "missing ISO_PATH $ISO_PATH"
  exit 1
fi

if [ ! -e "$DISK_IMAGE" ]; then
  usage
  echo "missing DISK_IMG $DISK_IMAGE"
  exit 1
fi

/usr/bin/expect -f - <<EOF
set timeout 10

# boot install iso and wait for installation to complete.
spawn /usr/libexec/qemu-kvm -boot order=d -cdrom $ISO_PATH -m 1024 -nographic -vga none -device sga -hda $DISK_IMAGE -no-reboot -device virtio-rng-pci -enable-fips

send_user "waiting for boot menu\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "Press Tab for full configuration options on menu items" {
    send_user "pressing tab to edit boot arguments\n"
    send -- "	"
  }
}

send_user "waiting to edit boot arguments\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "vmlinuz" {
    send_user "adding console=ttyS0 to boot arguments\n"
    send -- " console=ttyS0\r"
  }
}

set timeout 18000
expect {
  timeout { send_user "install did not complete in 5 hours"; exit 1 }
  eof { send_user "got eof on install step" }
  "reboot" { send_user "got reboot message" }
}

wait

# first boot after installation.  reboot occurs because of policy relabel.
spawn /usr/libexec/qemu-kvm -boot order=c -m 1024 -nographic -vga none -device sga -hda $DISK_IMAGE -no-reboot -device virtio-rng-pci -enable-fips

set timeout 18000
expect {
  timeout { send_user "first boot did not complete in 5 hours"; exit 1 }
  eof { send_user "got eof on first boot step" }
  "Restarting system" { send_user "got reboot message" }
}

wait
EOF
