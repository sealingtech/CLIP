# Copyright (C) 2012 Tresys Technology, LLC
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
auth --useshadow --passalgo=sha512

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
selinux-policy-mcs
selinux-policy-mcs-aide
selinux-policy-mcs-ssh
selinux-policy-mcs-unprivuser
#selinux-policy-mcs-ec2ssh
selinux-policy-mcs-config-strongswan
selinux-policy-mcs-vpnadm
clip-miscfiles

%end

%post --interpreter=/bin/bash
# DO NOT REMOVE THE FOLLOWING LINE. NON-EXISTENT WARRANTY VOID IF REMOVED.
#CONFIG-BUILD-PLACEHOLDER
export PATH="/sbin:/usr/sbin:/usr/bin:/bin:/usr/local/bin"
exec >/root/clip-post-install.log.log 2>&1
if [ x"$CONFIG_BUILD_LIVE_MEDIA" != "xy" ] \
        && [ x"$CONFIG_BUILD_AWS" != "xy" ];
then
        # Print the log to tty7 so that the user know what's going on
        tail -f /root/clip-post-install.log.log >/dev/tty7 &
        TAILPID=$!
        chvt 7
fi


echo "Installation timestamp: `date`" > /root/clip-info.txt
echo "#CONFIG-BUILD-PLACEHOLDER" >> /root/clip-info.txt

# Do not remove this line unless you remove all the other stanard include files below
# as they rekly on things defined in this include
%include includes/prep-post-env

%include includes/early-scap-audit
%include includes/scap-remediate
# if we are using firewalld, enable the base settings
if [ x"$CONFIG_ENABLE_FIREWALLD" == "xy" ]; then
%include includes/fix-firewalld
fi

if [ x"$CONFIG_BUILD_AWS" != "xy" -o x"$CONFIG_BUILD_VPN_ENABLE_TOOR" == "xy" ]; then
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

	if [ x"$CONFIG_BUILD_AWS" != "xy" ]; then
		chage -d 0 "$USERNAME"
	fi
	
	# Add the user to sudoers and setup an SELinux role/type transition.
	# This line enables a transition via sudo instead of requiring sudo and newrole.
	if [ x"$CONFIG_BUILD_UNCONFINED_TOOR" == "xy" ]; then
		echo "$USERNAME        ALL=(ALL) ROLE=toor_r TYPE=toor_t      ALL" >> /etc/sudoers
	else
		echo "$USERNAME        ALL=(ALL) ROLE=sysadm_r TYPE=sysadm_t      ALL" >> /etc/sudoers
	fi
fi

# Lock the root acct to prevent direct logins
usermod -L root

# default network settings
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

# You can remove this if you'd prefer a
# more graphical boot that also hides boot-time
# messages
%include includes/disable-graphical-boot

%include includes/fix-bad-scap
%include includes/gui-config
%include includes/late-scap-audit
%include includes/set-enforcement-mode

echo "session optional pam_umask.so umask=0077" >> /etc/pam.d/sshd


# Turn on IPV4 forwarding
sed -i 's/net.ipv4.ip_forward = 0/net.ipv4.ip_forward = 1/' /etc/sysctl.conf
sed -i 's/net.ipv4.ip_no_pmtu_disc = 0//' /etc/sysctl.conf
echo "net.ipv4.ip_no_pmtu_disc = 1" >> /etc/sysctl.conf

#####IPtables Configuration#####
cat << EOF > /etc/sysconfig/iptables
*mangle
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
-A FORWARD -o eth0 -p tcp -m tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1361:1536 -j TCPMSS --set-mss 1360
COMMIT
*nat
:PREROUTING ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A POSTROUTING -j MASQUERADE 
COMMIT
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 22 -j ACCEPT
-A INPUT -p udp -m udp --dport 500 -j ACCEPT
-A OUTPUT -p udp -m udp --sport 500 -j ACCEPT
-A INPUT -p udp -m udp --dport 4500 -j ACCEPT
-A OUTPUT -p udp -m udp --sport 4500 -j ACCEPT
COMMIT
EOF

cat << EOF > /etc/sysconfig/ip6tables
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
COMMIT
EOF

#####IPtables End Configuration#####

# turn on the configure-strongswan service
chkconfig --level 34 configure-strongswan on

# Turn strongswan on in AWS as it will be configured by the scripts above.
chkconfig strongswan on

PASSWORD="neutronbass"
HASHED_PASSWORD='$6$314159265358$ytgatj7CAZIRFMPbEanbdi.krIJs.mS9N2JEl0jkPsCvtwC15z07JLzFLSuqiCdionNZ1XNT3gPKkjIG0TTGy1'

# we need to be vpnadm_u:vpnadm_r:vpnadm_t
useradd -m vpn
semanage user -N -a -R vpnadm_r vpnadm_u
semanage login -N -a -s vpnadm_u vpn
usermod -s /usr/bin/strongswan_login.py vpn
usermod --pass="$HASHED_PASSWD" 
chage -E -1 vpn

useradd -m sftp
semanage login -N -a -s vpnadm_u sftp
usermod -d /sftp sftp
#the above usermod line mucks up file_contexts.homedirs, fix it
semanage fcontext -a -e /sftp /home/sftp
usermod --pass="$HASHED_PASSWORD" sftp
chage -E -1 sftp

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

	# disable password auth
	sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config

	# turn on the ssh key script
	chkconfig --level 34 ec2-get-ssh on

	# if you're the Government deploying to AWS and want to monitor people feel free to remove these lines.
	# But for our purposes, we explicitly don't want monitoring or logging
	> /etc/issue
	> /etc/issue.net
	#well logs are still useful for debugging purposes :)
	if [ x"$CONFIG_BUILD_VPN_ENABLE_TOOR" != "xy" ]
	then
                chkconfig rsyslog off
                chkconfig auditd off
                # TODO: this should really be done via policy
                # the #*/ makes vim highlighting normal again (or as normal as it is for a ks)
                rm -rf /var/log/* #*/
                touch /var/log/{yum.log,boot.log,secure,spooler,btmp,lastlog,utmp,wtmp,dmesg,maillog,messages,cron,audit/audit.log}
                chmod 000 /var/log/* #*/
                chattr +i /var/log/{yum.log,boot.log,secure,spooler,btmp,lastlog,utmp,wtmp,dmesg,maillog,messages,cron,audit/audit.log}
                rm -rf /root/* #*/
	fi

	SSH_USERS="sftp vpn"

	if [ x"$CONFIG_BUILD_VPN_ENABLE_TOOR" == "xy" ]
	then
		SSH_USERS="$SSH_USERS toor"
		chage -E -1 $USERNAME 
	fi
	sed -i -e "s/__USERS__/$SSH_USERS/g" /etc/rc.d/init.d/ec2-get-ssh

	cat << EOF > /etc/sysconfig/iptables
*mangle
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
-A FORWARD -o eth0 -p tcp -m tcp --tcp-flags SYN,RST SYN -m tcpmss --mss 1301:1536 -j TCPMSS --set-mss 1300
COMMIT
*nat
:PREROUTING ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A POSTROUTING -j MASQUERADE 
COMMIT
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 22 -j ACCEPT
-A INPUT -p udp -m udp --dport 500 -j ACCEPT
-A OUTPUT -p udp -m udp --sport 500 -j ACCEPT
-A INPUT -p udp -m udp --dport 4500 -j ACCEPT
-A OUTPUT -p udp -m udp --sport 4500 -j ACCEPT
-A INPUT -p tcp -m tcp --sport 80 -s 169.254.169.254 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 80 -d 169.254.169.254 -j ACCEPT
COMMIT
EOF

elif [ x"$CONFIG_BUILD_LIVE_MEDIA" == "xy" ]; then
        chage -E -1 $USERNAME

else
	rpm -e selinux-policy-mcs-ec2ssh 2>&1 >/dev/null
fi

sed -i -e 's;.*AuthorizedKeysFile.*;AuthorizedKeysFile /home/%u/.ssh/authorized_keys;' /etc/ssh/sshd_config

#make sure you're using the internal sftp
sed -i -r -e "s/Subsystem\s*sftp.*//g" /etc/ssh/sshd_config

echo -e "Subsystem sftp internal-sftp\n" >> /etc/ssh/sshd_config
echo -e "Match Group sftp\n" >> /etc/ssh/sshd_config
echo -e "        AllowTCPForwarding no\n" >> /etc/ssh/sshd_config
echo -e "        X11Forwarding no\n" >> /etc/ssh/sshd_config
echo -e "        ChrootDirectory /home\n" >> /etc/ssh/sshd_config
echo -e "        ForceCommand internal-sftp\n" >> /etc/ssh/sshd_config

semanage boolean -N -S ${POLNAME} -m --on ssh_chroot_rw_homedirs

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

kill $TAILPID 2>/dev/null 1>/dev/null
kill $(jobs -p) 2>/dev/null 1>/dev/null

chvt 6

%end

