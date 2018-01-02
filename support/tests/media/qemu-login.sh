#!/bin/bash

########
# expect script to smoke test CLIP install ISO
# by: booting installed VM with qemu,
# logging in as toor, and running shutdown


usage() {
  echo "usage: $0 DISK_IMG"
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

DISK_IMAGE="$1"

if [ ! -e "$DISK_IMAGE" ]; then
  echo "error: missing disk image $DISK_IMAGE"
  exit 1
fi

/usr/bin/expect -f - <<EOF
# first full boot
spawn /usr/libexec/qemu-kvm -boot order=c -m 1024 -nographic -vga none -device sga -hda $DISK_IMAGE -no-reboot -device virtio-rng-pci -enable-fips

set timeout 300
send_user "waiting for login prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "login: " {
    sleep 1
    send_user "sending username\n"
    send -- "toor\r"
  }
}

set timeout 10
send_user "waiting for password prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "Password: " {
    sleep 1
    send_user "sending password\n"
    send -- "neutronbass\r"
  }
}

send_user "waiting for password change prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  -re "You are required to change your password immediately.*current.*password: " {
    sleep 1
    send_user "sending password again"
    send -- "neutronbass\r"
  }
}

send_user "waiting for new password prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "New password: " {
    sleep 1
    send_user "sending new password"
    send -- "1234qwer!@#\\\$QWER\r"
  }
}

send_user "waiting for new password confirmation prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "Retype new password: " {
    sleep 1
    send_user "sending new password confirmation"
    send -- "1234qwer!@#\\\$QWER\r"
  }
}

send_user "waiting for command prompt\n"
expect {
  default { send_user "\nerror: timeout or eof encountered\n"; exit 1 }
  "$ " {
    send_user "sending id command\n"
    send -- "id -Z\r"
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
    send -- "1234qwer!@#\\\$QWER\r"
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
