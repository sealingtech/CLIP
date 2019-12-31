# Copyright (C) 2012 Tresys Technology, LLC
# Copyright (C) 2014 Quark Security, Inc
#
# Authors:	Spencer Shimko <spencer@quarksecurity.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1) Distributed source includes this license and disclaimer,
# 2) Binary distributions must reproduce the license and disclaimer in the 
#    documentation and/or other materials provided with the distribution,
# 3) Tresys and contributors may not be used to endorse or promote products 
#    derived from this software without specific prior written permission
#
# THIS SOFTWARE IS PROVIDED BY TRESYS ``AS IS'' AND ANY EXPRESS OR IMPLIED 
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO 
# EVENT SHALL  TRESYS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND 
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#################### START CLIP CONFIGURATION ######################
# SEARCH THIS FILE FOR "FIXME" AND YOU WILL FIND THE FIELDS YOU
# NEED TO ADJUST.
#

# FIXME: Set your initial bootloader password below.
bootloader --location=mbr --timeout=5 --append="audit=1" --password=neutronbass

# FIXME: Change the root password.
#        CLIP locks the root account in the post below so this password won't 
#        work.  However, if the field is missing you will be prompted during 
#        installation for a password so specify one to avoid install-time 
#        questions.
# rootpw correctbatteryhorsestaple
rootpw neutronbass

lang en_US.UTF-8
keyboard us

#text - is broken bz 785400 anaconda abrt - No module named textw.netconfig_text
cdrom
install
timezone --utc Etc/GMT

selinux --enforcing
firewall --enabled
reboot --eject

# DO NOT REMOVE THE FOLLOWING LINE. NON-EXISTENT WARRANTY VOID IF REMOVED.
#REPO-REPLACEMENT-PLACEHOLDER

%include includes/storage

%packages --excludedocs
%include includes/packages
%include includes/gui-packages
#CONFIG-BUILD-ADDTL-PACKAGES
selinux-policy
# rhel8 does not appear to build an mcs package
# but the targeted package is built as mcs
#selinux-policy-mcs
#selinux-policy-mcs-ssh
#selinux-policy-mcs-unprivuser
#selinux-policy-mcs-aide
#selinux-policy-mcs-ec2ssh
clip-miscfiles


%end

%post --interpreter=/bin/bash
# DO NOT REMOVE THE FOLLOWING LINE. NON-EXISTENT WARRANTY VOID IF REMOVED.
#CONFIG-BUILD-PLACEHOLDER

# Do not remove this line unless you remove all the other stanard include files below
# as they rekly on things defined in this include
%include includes/prep-post-env

set -x

%include includes/early-scap-audit
%include includes/scap-remediate

# FIXME: Change the username and password.
#        If a hashed password is specified it will be used
#        and the PASSWORD field will be ignored.
#
#        To generate a SHA512 hashed password try something like this:
#           python -c "import crypt; print crypt.crypt('neutronbass', '\$6\$314159265358\$')"
#        Note that the "\$6" indicates it is SHA512 and must remain in place.
#        Further, make sure you specify a salt such as "314159265358."
#        Finally, make sure the hashed password is in single quotes to prevent expansion of the dollar signs.
USERNAME="toor"
PASSWORD="neutronbass"
HASHED_PASSWORD='$6$314159265358$ytgatj7CAZIRFMPbEanbdi.krIJs.mS9N2JEl0jkPsCvtwC15z07JLzFLSuqiCdionNZ1XNT3gPKkjIG0TTGy1'

######## START DEFAULT USER CONFIG ##########
# NOTE: The root account is *locked*.  You must create an unprivileged user 
#       and grant that user administrator capabilities through sudo.
#       An account will be created below.  This account will be allowed to 
#       change to the SELinux system administrator role, and become root via 
#       sudo.  The information used to create the account comes from the 
#       USERNAME and PASSWORD values defined a few lines above.
#
# Don't get lost in the 'if' statement - basically map $USERNAME to the unconfined toor_r:toor_t role if it is enabled.  
if [ x"$CONFIG_BUILD_UNCONFINED_TOOR" == "xy" ]; then
	semanage user -N -a -R toor_r -R staff_r -R sysadm_r -R system_r "${USERNAME}_u" 
else
	semanage user -N -a -R staff_r -R sysadm_r -R system_r "${USERNAME}_u" || semanage user -a -R staff_r -R system_r "${USERNAME}_u"
fi
useradd -m "$USERNAME" -G wheel
semanage login -N -a -s "${USERNAME}_u" "${USERNAME}"

if [ x"$HASHED_PASSWORD" == "x" ]; then
	passwd --stdin "$USERNAME" <<< "$PASSWORD"
else
	usermod --pass="$HASHED_PASSWORD" "$USERNAME"
fi

# Add the user to sudoers and setup an SELinux role/type transition.
# This line enables a transition via sudo instead of requiring sudo and newrole.
if [ x"$CONFIG_BUILD_UNCONFINED_TOOR" == "xy" ]; then
	echo "$USERNAME        ALL=(ALL) ROLE=toor_r TYPE=toor_t      ALL" >> /etc/sudoers
else
	echo "$USERNAME        ALL=(ALL) ROLE=sysadm_r TYPE=sysadm_t      ALL" >> /etc/sudoers
fi

# Lock the root acct to prevent direct logins
usermod -L root

######## END DEFAULT USER CONFIG ##########

if [ x"$CONFIG_BUILD_AWS" == "xy" -o x"$CONFIG_BUILD_ENABLE_DHCP" == "xy" ]; then
cat << EOF > /etc/sysconfig/network-scripts/ifcfg-eth0
DEVICE=eth0
TYPE=Ethernet
ONBOOT=yes
NM_CONTROLLED=yes
BOOTPROTO=dhcp
IPV6_PRIVACY=rfc3041
EOF
fi

echo "Turning sshd off"
/sbin/chkconfig --level 0123456 sshd off

# You can remove this if you'd prefer a
# more graphical boot that also hides boot-time
# messages
%include includes/disable-graphical-boot

%include includes/fix-bad-scap
%include includes/gui-config
%include includes/late-scap-audit
%include includes/set-enforcement-mode

# Need to do some additional customizations if we're building for AWS
if [ x"$CONFIG_BUILD_AWS" == "xy" ]; then

        #set up /etc/ftsab
        sed -i -e "s/\/dev\/root/\/dev\/xvde1/" /etc/fstab
        mkdir -p /boot/grub

        #set up /boot/grub/menu.lst
        echo "default=0" >> /boot/grub/menu.lst
        echo -e "timeout=0\n" >> /boot/grub/menu.lst
        echo "title CLIP-KERNEL" >> /boot/grub/menu.lst
        echo "        root (hd0)" >> /boot/grub/menu.lst
        KERNEL=`find /boot -iname vmlinuz*`
        INITRD=`find /boot -iname initramfs*`
        echo "        kernel $KERNEL ro root=/dev/xvde1 rd_NO_PLYMOUTH" >> /boot/grub/menu.lst
        echo "        initrd $INITRD" >> /boot/grub/menu.lst

        # turn on the ssh key script
        chkconfig --level 34 ec2-get-ssh on
	/sbin/chkconfig sshd on

        # disable password auth
        sed -i -e "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config

	sed -i -e "s/__USERNAME__/${USERNAME}/g" /etc/rc.d/init.d/ec2-get-ssh
	
	# if you're the Government deploying to AWS and want to monitor people feel free to remove these lines.
	# But for our purposes, we explicitly don't want monitoring or logging
	> /etc/issue
	> /etc/issue.net

	chage -E -1 "$USERNAME"

	cat << EOF > /etc/sysconfig/iptables
*mangle
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
COMMIT
*nat
:PREROUTING ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
COMMIT
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 22 -j ACCEPT
-A INPUT -p tcp -m tcp --sport 80 -s 169.254.169.254 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 80 -d 169.254.169.254 -j ACCEPT
COMMIT
EOF

elif [ x"$CONFIG_BUILD_LIVE_MEDIA" == "xy" ]; then
        chage -E -1 $USERNAME
else
	rpm -q selinux-policy-mcs-ec2ssh >/dev/null && rpm -e selinux-policy-mcs-ec2ssh 2>&1 > /dev/null
	chage -d 0 "$USERNAME"
fi

cat << EOF > /etc/sysconfig/ip6tables
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
COMMIT
EOF

cat << EOF > /etc/sysconfig/iptables
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
COMMIT
EOF

# This is rather unfortunate, but the remediation content
# starts services, which need to be killed/shutdown if
# we're rolling Live Media.  First, kill the known
# problems cleanly, then just kill them all and let
# <deity> sort them out.
if [ x"$CONFIG_BUILD_LIVE_MEDIA" == "xy" ] \
        || [ x"$CONFIG_BUILD_AWS" == "xy" ]; then
	rm /.autorelabel
	# this unfortunate hack is b/c stopping the daemon only
	# kills the first process and the child hangs around 
	# and has open FDs and the img file can't be cleanly 
	# unmounted
	kill -TERM -`cat /var/run/ntpd.pid`
fi

# Mitigate CVE-2016-0777
echo "UseRoaming no" >> /etc/ssh/ssh_config

kill $(jobs -p) 2>/dev/null 1>/dev/null
kill $TAILPID 2>/dev/null 1>/dev/null

echo "Done with post install scripts..."

chvt 6


%end

