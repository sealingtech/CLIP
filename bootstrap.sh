#!/bin/bash -u
# Copyright (C) 2013 Quark Security, Inc
# Copyright (C) 2013 Cubic Corporation
#
# Authors: Spencer Shimko <spencer@quarksecurity.com>
set -e

rhn_subscribe() {
	# If we are building on a redhat machine register with subscription manager

	# Ask the user to set their hostname since it shows up in the user's rhel subscription
	read -r -p "Your current hostname is \"$(hostname)\", would you like to change it before subscribing? [y/N] " confirmation
	case "$confirmation" in
		[yY][eE][sS]|[yY])
			/bin/echo -e "Enter a new hostname for the system.\n"
			read hostname
			/bin/hostnamectl set-hostname "$hostname"
			;;
	esac

	# Check to see if the host is subscripted, if not subscribe them
	if /bin/subscription-manager status | /bin/grep -q "Overall Status: Unknown"; then
		/bin/subscription-manager register
	fi

	# Check to see if the host is attached to a license, if not attach them
	if /bin/subscription-manager list --consumed | /bin/grep -q "No consumed subscription pools"; then
		/bin/echo -e "This host requires a license. Please select from the following list of pools which one you want to attach to.\n"
		/bin/subscription-manager list --available | /bin/grep -e "Subscription Name:" -e "Pool ID:" -e "Available:" -e "System Type:"  --color=never
		/bin/echo -e "\nWhich pool ID would you like to attach to?"
		read pool_id
		/bin/subscription-manager attach --pool="$pool_id"
	fi

	if [ "$major_version" -eq 7 ]; then
		# Enable the required optional repo
		/bin/subscription-manager repos --enable=rhel-7-*-optional-rpms
	fi
}


set_selinux_permissive() {
	#Make selinux permissive due to requirements of build tools
	/usr/sbin/setenforce 0
	/bin/sed -i -e 's/^SELINUX=.*/SELINUX=permissive/' /etc/selinux/config
}

get_os_major_version() {
	local full_version=$(rpm -q --whatprovides --queryformat '%{version}' system-release)
	echo -n ${full_version:0:1}
}

# make sure the system is a supported version
major_version=$(get_os_major_version)
if [ -z "$major_version" ]; then
	echo "error: unable to detect OS major version.  is this a rhel or centos system?"
	exit 1
fi
if [ "$major_version" != "8" -a "$major_version" != 7 ]; then
	echo "error: unsupport OS major version ${major_version}.  supported versions are 7 and 8"
	exit 1
fi

if [ $EUID -ne 0 ]; then
	echo "The bootstrap script requires root; try re-running with sudo."
	exit
fi

if [ $# -eq 2 ] && [ $1 == "-c" ] && [ ! -z $2 ]; then
	config_var=""
	config_val=""
	distro_flag=false
	#Use two arrays since we don't know whether the config acutally makes sense
	distro=""
	declare -a repo_names
	declare -a repo_paths
	while read -r line;
	do
		if [[ ${line} =~ ^(.*)=(.*)$ ]]; then
			config_var="${BASH_REMATCH[1]}"
			config_val="${BASH_REMATCH[2]}"
			echo "Read config setting ${config_var} and value ${config_val}"
			case ${config_var} in
				repo_name)
					if [ -z "${config_val}" ]; then
						echo "Invalid repo name: Name must not be empty"
						exit 1
					else
						repo_names+=("${config_val}")
						echo ${repo_names[@]}
					fi
					;;
				repo_path)
					if [[ -z "${config_val}" || ! -d "${config_val}" ]]; then
						echo "Invalid repo path: Specify a valid repo directory"
						exit 1
					else
						repo_paths+=("${config_val}")
						echo ${repo_paths[@]}
					fi
					;;
				distro)
					if ${distro_flag} ; then
						echo "Ignoring redundant distro configuration value"
					else
						if [[ ! ${config_val} =~ ^(r|c)$ ]]; then
							echo "Invalid Distro: specify r for redhat and c for centos"
							exit 1
						else
						distro="${config_val}"
						distro_flag=true
						fi
					fi
					;;
			esac
		else
			echo "Read invalid line ${line}; all lines should be key=value format"
			exit 1
		fi
	done < $2
	if [ ${#repo_names[@]} -ne ${#repo_paths[@]} ]; then
		echo "All repos specified must have a name and a path"
		exit 1
	fi
	#Add repos to config file
	repo_count=${#repo_names[@]}
	tmpfile=`/bin/mktemp`
	/bin/cat CONFIG_REPOS | /bin/sed -e 's/^\([a-zA-Z0-9].*\)$/#\1/' > $tmpfile
	echo -e "# INSERTED BY BOOTSTRAP.SH" >> ${tmpfile}
	echo "Appending $repo_count repos"
	for (( i=0; i<${repo_count}; i++)); do
		echo "Adding repos ${repo_names[$i]}"
		echo "${repo_names[$i]}=${repo_paths[$i]}" >> ${tmpfile}
	done
	mv $tmpfile CONFIG_REPOS
	chown ${SUDO_USER}:${SUDO_USER} CONFIG_REPOS
	case $distro in
		r)
			echo "Using distro: Redhat"
			echo "Registration via bootstrap strip not currently supported for RHEL 7 please register manually using subscription-manager"
			#rhn_subscribe
			;;
		c)
			echo "Using distro: Centos"
			#No centos specific steps for now
			;;
		[^cr])
			echo "Unsupported Distro"
			;;
	esac
	set_selinux_permissive
else
	/bin/echo -e "Creating an environment for building software and ISOs can be a little
complicated.  This script will automate some of those tasks.  Keep in mind that
this script isn't exhaustive; depending on a variety of factors you may have to
install some additional packages.\n\nYour user *must* have sudo access for any
of this to work.

If you are using RHEL enter 'r'.
If you are using CentOS 'c'."

	read distro

	tmpfile=''
	while :; do
		/bin/echo -e "Enter a name for this yum repo.  Just leave empty if you are done adding, or don't wish to change the repositories.\n"
		read name
		[ x"$name" == "x" ] && break
		/bin/echo -e "Enter a fully qualified path for this yum repo.  Just leave empty if you are done adding, or don't wish to change the repositories.\n"
		read path
		[ x"$path" == "x" ] && break

		if [ x"$tmpfile" == "x" ]; then
			tmpfile=`/bin/mktemp`
			/bin/cat CONFIG_REPOS | /bin/sed -e 's/^\([a-zA-Z0-9].*\)$/#\1/' > $tmpfile
		fi
		/bin/echo -e "# INSERTED BY BOOTSTRAP.SH\n$name = $path" >> $tmpfile
	done

	if [ x"$tmpfile" != "x" ]; then
		mv $tmpfile CONFIG_REPOS
		chown ${SUDO_USER}:${SUDO_USER} CONFIG_REPOS
	fi

	# if we're on RHEL add the Opt channel
	if [ "$distro" == "r" ]; then
		/bin/echo "We're going to try to subscribe to the RHEL Optional channel for your distro.
This might not work if you don't have credentials or you're out of entitlements.
We *NEED* packages from Opt to be installed on the build host *and* need to pull
packages from there to put on the generated installable media.  If you're using
RHEL and want to work-around this issue (hack):
1. Grab a CentOS ISO.
2. Mount it.
3. Add it as a yum repo:
	http://docs.oracle.com/cd/E37670_01/E37355/html/ol_create_repo.html
4. Re-run this script and pick CentOS.
5. Refer to the same path in the CONFIG_REPOS file.
Press enter to continue."

	read
		rhn_subscribe
	fi

	/bin/echo -e "This is embarassing but due to a bug (bz #861281) you must do builds in permissive.\nhttps://bugzilla.redhat.com/show_bug.cgi?id=861281"
	/bin/echo "So this is a heads-up we're going to configure your system to run in permissive mode.  Sorry!"
	/bin/echo "Press enter to continue."
	read
	set_selinux_permissive

fi

# install packages that we need but aren't commonly present on default RHEL installs.
all_needed_packages=$(./support/get-host-deps.sh yum)
needed_packages=""
for i in $all_needed_packages; do
	if ! /bin/rpm -q "$i" >/dev/null; then
	       needed_packages="$needed_packages $i"
       fi
done
if [ -n "$needed_packages" ]; then
	/usr/bin/yum install -y $needed_packages
fi

# install packages that we carry in CLIP
/usr/bin/yum -y localinstall host_packages/${major_version}/*/*.rpm

# add us to the mock group
/bin/echo "Adding user to mock group and configuring sudo."
/usr/sbin/usermod -aG mock ${SUDO_USER}

# set it up so mock members dont need to enter a pw
# this isnt ideal but noone sits around waiting for a CLIP build to
# prompt for a pw, and sudo will timeout and the build is borked.
/bin/echo "%mock   ALL=(ALL)       NOPASSWD: ALL" | (sudo su -c 'EDITOR="tee -a" visudo -f /etc/sudoers.d/mock >/dev/null')


/bin/echo "Basic bootstrapping of build host is complete."
/bin/echo "Run '/usr/bin/newgrp mock' as your unprivileged user then"
/bin/echo "run 'make clip-minimal-inst-iso' to build the minimal CLIP installation ISO."

exit 0
