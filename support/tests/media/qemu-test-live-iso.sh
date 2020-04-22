#!/bin/bash

########
# expect script to smoke test CLIP live ISO
# by: booting ISO with qemu, logging in as toor,
# and running shutdown


usage() {
  echo "usage: $0 ISO_PATH"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

ISO_PATH="$1"

if [ ! -e "$ISO_PATH" ]; then
  usage
  echo "missing ISO_PATH $ISO_PATH"
  exit 1
fi

/usr/bin/expect -f - <<EOF
set timeout 10

spawn /usr/libexec/qemu-kvm -boot d -cdrom $ISO_PATH -m 512 -nographic -vga none -device sga

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
  "vmlinuz0" {
    send_user "adding console=ttyS0 to boot arguments\n"
    send -- " console=ttyS0\r"
  }
}

set timeout 500
send_user "waiting for login prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "login: " {
    sleep 1
    send_user "sending username\n"
    send -- "toor\r"
  }
}

set timeout 30
send_user "waiting for password prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "Password: " {
    sleep 1
    send_user "sending password\n"
    send -- "neutronbass\r"
  }
}

send_user "waiting for command prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "$ " {
    send_user "sending shutdown command\n"
    send -- "sudo shutdown -h now\r"
  }
}

send_user "waiting for password request from sudo\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "password for toor:" {
    sleep 1
    send_user "sending password\n"
    send -- "neutronbass\r"
  }
}

set timeout 300
send_user "waiting for power down\n"
expect {
  eof { send_user "got eof\n" }
  timeout { send_user "\nerror: timeout while waiting for power off\n"; exit 1 }
  "Powering off." { send_user "got powering off message\n" }
}

wait
EOF

