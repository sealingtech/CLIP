# Copyright (C) 2012 Tresys Technology, LLC
# Copyright (C) 2014 Quark Security, Inc
#
# Authors:	Spencer Shimko <spencer@quarksecurity.com>
#		John Feehley <jfeehley@quarksecurity.com>
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
timezone --utc Etc/GMT-5
auth --useshadow --passalgo=sha512

selinux --enforcing
firewall --enabled
reboot --eject

# DO NOT REMOVE THE FOLLOWING LINE. NON-EXISTENT WARRANTY VOID IF REMOVED.
#REPO-REPLACEMENT-PLACEHOLDER

%include includes/standard-storage

%packages --excludedocs
%include includes/standard-packages
#CONFIG-BUILD-ADDTL-PACKAGES
selinux-policy
selinux-policy-mcs
selinux-policy-mcs-apache
selinux-policy-mcs-mysql
selinux-policy-mcs-ssh
selinux-policy-mcs-postfix
#selinux-policy-mcs-ec2ssh
clip-miscfiles
webpageexample
clip-dracut-module
mod_ssl

mariadb
mariadb-server
httpd
php
php-common
php-mysql
#####

%end

%post --interpreter=/bin/bash
# DO NOT REMOVE THE FOLLOWING LINE. NON-EXISTENT WARRANTY VOID IF REMOVED.
#CONFIG-BUILD-PLACEHOLDER
export PATH="/sbin:/usr/sbin:/usr/bin:/bin:/usr/local/bin"
exec >/root/clip_post_install.log 2>&1
if [ x"$CONFIG_BUILD_LIVE_MEDIA" != "xy" ] \
        && [ x"$CONFIG_BUILD_AWS" != "xy" ];
then
        # Print the log to tty7 so that the user know what's going on
        tail -f /root/clip_post_install.log >/dev/tty7 &
        TAILPID=$!
        chvt 7
fi

echo "Installation timestamp: `date`" > /root/clip-info.txt
echo "#CONFIG-BUILD-PLACEHOLDER" >> /root/clip-info.txt

# Do not remove this line unless you remove all the other stanard include files below
# as they rekly on things defined in this include
%include includes/standard-prep-post-env

%include includes/standard-early-scap-audit
%include includes/standard-scap-remediate

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
	semanage user -N -a -R toor_r -R staff_r -R sysadm_r "${USERNAME}_u" 
else
	semanage user -N -a -R staff_r -R sysadm_r "${USERNAME}_u" || semanage user -a -R staff_r "${USERNAME}_u"
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

# This remediation doesn't appear to be added to the script, it might have been added after the SSG release
# platform = Red Hat Enterprise Linux 6
# If system does not contain control-alt-delete.override,
if [ ! -f /etc/init/control-alt-delete.override ]; then

	# but does have control-alt-delete.conf file,
	if [ -f /etc/init/control-alt-delete.conf ]; then

		# then copy .conf to .override to maintain persistency
		cp /etc/init/control-alt-delete.conf /etc/init/control-alt-delete.override
	fi
fi
 
sed -i 's,^exec.*$,exec /usr/bin/logger -p authpriv.notice -t init "Ctrl-Alt-Del was pressed and ignored",' /etc/init/control-alt-delete.override

# also these PAM fixes aren't being remediated automatically
for file in /etc/pam.d/system-auth /etc/pam.d/password-auth-ac; do
	sed -i -e 's/^auth\s\+required\s\+pam_faillock.*/auth required pam_faillock.so preauth silent deny=3 unlock_time=604800 fail_interval=900/' $file
	sed -i -e 's/^auth\s\+\[default.*pam_faillock.*/auth [default=die] pam_faillock.so authfail deny=3 unlock_time=604800 fail_interval=900/'  $file
	# this already appears to be the default... false positive probably
	#sed -i -e 's/^account.*pam_unix.*/account required pam_faillock.so \n&/' $file

done

if grep -q "maxrepeat" /etc/pam.d/system-auth; then
	sed -i --follow-symlink "s/\(maxrepeat *= *\).*/\13/" /etc/pam.d/system-auth
else
	sed -i --follow-symlink "s/\(.*pam_cracklib\.so.*\)/\1 maxrepeat=3/" /etc/pam.d/system-auth
fi

usermod -s /sbin/nologin mysql

# We don't want the final remediation script to set the system to targeted
sed -i -e "s/SELINUXTYPE=${POLNAME}/SELINUXTYPE=targeted/" /etc/selinux/config

oscap xccdf eval --profile stig-rhel6-server-upstream \
--report /root/scap/post/html/report.html \
--results /root/scap/post/html/results.xml \
/usr/share/xml/scap/ssg/content/ssg-${xccdf}-xccdf.xml

oscap xccdf generate fix \
--result-id xccdf_org.open-scap_testresult_stig-rhel6-server-upstream \
/root/scap/post/html/results.xml > /root/scap/post/remediation-script.sh
chmod +x /root/scap/post/remediation-script.sh

sed -i -e "s/targeted/${POLNAME}/" /etc/selinux/config

# Now fix things that remediation might have broke


# Lock the root acct to prevent direct logins
usermod -L root


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

cat << EOF > /etc/sysconfig/iptables
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 80 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 443 -j ACCEPT
COMMIT
EOF

cat << EOF > /etc/sysconfig/ip6tables
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
COMMIT
EOF

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

	chage -E -1 $USERNAME

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
-A INPUT -p tcp -m tcp --sport 80 -s 169.254.169.254 -j ACCEPT
-A OUTPUT -p tcp -m tcp --dport 80 -d 169.254.169.254 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
-A INPUT -p tcp -m tcp --dport 443 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 22 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 80 -j ACCEPT
-A OUTPUT -p tcp -m tcp --sport 443 -j ACCEPT
COMMIT
EOF
elif [ x"$CONFIG_BUILD_LIVE_MEDIA" == "xy" ]; then
	chage -E -1 $USERNAME
else
        rpm -e selinux-policy-mcs-ec2ssh
        chage -d 0 "$USERNAME"
	/sbin/chkconfig sshd off
fi

chkconfig httpd on

cat << EOF > /etc/sysconfig/ip6tables
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT DROP [0:0]
COMMIT
EOF

sed -i -e 's/.*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i -e 's/#\s*RSAAuthentication .*/RSAAuthentication yes/' /etc/ssh/sshd_config
sed -i -e 's/#\s*PubkeyAuthentication .*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sed -i -e 's/GSSAPIAuthentication .*/GSSAPIAuthentication no/g' /etc/ssh/sshd_config

# You can remove this if you'd prefer a
# more graphical boot that also hides boot-time
# messages
%include includes/disable-graphical-boot

%include includes/standard-fix-bad-scap
%include includes/standard-late-scap-audit
%include includes/standard-set-enforcement-mode

# starts services, which need to be killed/shutdown if
# we're rolling Live Media.  First, kill the known
# problems cleanly, then just kill them all and let
# <deity> sort them out.
if [ x"$CONFIG_BUILD_LIVE_MEDIA" == "xy" ] \
        || [ x"$CONFIG_BUILD_AWS" == "xy" ]; then
	rm -f /.autorelabel
	# this unfortunate hack is b/c stopping the daemon only
	# kills the first process and the child hangs around 
	# and has open FDs and the img file can't be cleanly 
	# unmounted
	kill -TERM -`cat /var/run/ntpd.pid`
fi

# Mitigate CVE-2016-0777
echo "UseRoaming no" >> /etc/ssh/ssh_config

# this one isn't actually due to remediation, but needs to be done too
kill $(jobs -p) 2>/dev/null 1>/dev/null
kill $TAILPID 2>/dev/null 1>/dev/null

echo "Done with post install scripts..."

%end

%post --nochroot

# DO NOT REMOVE THE FOLLOWING LINE. NON-EXISTENT WARRANTY VOID IF REMOVED.
#CONFIG-BUILD-PLACEHOLDER

if [ x"$CONFIG_BUILD_PRODUCTION" == "xy" ]; then
    echo "Deleting anaconda-ks.cfg as this is a production build" >> /mnt/sysimage/root/clip_post_install.log
    rm /mnt/sysimage/root/anaconda-ks.cfg
fi

%end
