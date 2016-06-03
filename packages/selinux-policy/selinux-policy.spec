%define distro redhat 
%define polyinstatiate n
%define monolithic n
%define POLICYVER 29
%define POLICYCOREUTILSVER 2.1.14-74
%define CHECKPOLICYVER 2.1.12-3
Name:   %{pkgname}
Version: %{version}
Release: %{release}
Summary: Policy Base Configuration Data
License: GPLv2+
Group: System Environment/Base
Source: %{pkgname}-%{version}.tar.gz
Url: http://oss.tresys.com/repos/refpolicy/
BuildArch: noarch
Requires: coreutils

%description 
This package contains the base components common across policy types.  In
addition to this package, you will want to choose from:
selinux-policy-mcs (an MCS policy)
selinux-policy-mls (an MLS policy)

%files 
%defattr(-,root,root,-)
%{_mandir}/man*/*
# policycoreutils owns these manpage directories, we only own the files within them
%{_mandir}/ru/*/*
%dir %{_usr}/share/selinux
%dir %{_usr}/share/selinux/devel
%dir %{_usr}/share/selinux/packages
%dir %{_sysconfdir}/selinux
%ghost %config(noreplace) %{_sysconfdir}/selinux/config
%ghost %{_sysconfdir}/sysconfig/selinux
%{_usr}/share/selinux/devel/Makefile
%{_usr}/share/selinux/devel/example.*
%{_usr}/share/selinux/devel/policy.*

%package doc
Summary: SELinux policy documentation
Group: System Environment/Base
Requires(pre): selinux-policy = %{version}-%{release}
Requires: /usr/bin/xdg-open
BuildRequires: policycoreutils-python m4 policycoreutils python make gcc checkpolicy >= %{CHECKPOL_VERSION} policycoreutils-devel

%description doc
Policy documentation

%files doc
%defattr(-,root,root,-)
%doc %{_usr}/share/doc/%{name}-%{version}
%doc %{_usr}/share/selinux/devel/html
%attr(755,root,root) %{_usr}/share/selinux/devel/policyhelp

%global genSeparatePolRPM() \
%package %2-%1 \
Summary: SELinux %2 policy for %1 \
Group: System Environment/Base \
Requires(pre): selinux-policy-%2 = %{version}-%{release} \
BuildRequires: policycoreutils-python m4 policycoreutils python make gcc checkpolicy >= %{CHECKPOL_VERSION} \
\
%description %2-%1  \
SELinux %2 policy for %1 \
\
%files %2-%1 \
%{_usr}/share/selinux/%2/%1.pp \
\
%post %2-%1 \
echo %1.pp >> %{_usr}/share/selinux/%2/modules.lst \
semodule -n -s %2 -i %{_usr}/share/selinux/%2/%1.pp \
echo "NOTE: installing the %1 policy RPM *does not reload the policy*." \
echo "To reload the policy run 'semodule -R'" 

%{expand:%( for f in %{separatePkgs}; do echo "%%genSeparatePolRPM $f mcs"; done)}

%{expand:%( for f in %{separatePkgs}; do echo "%%genSeparatePolRPM $f mls"; done)}

%define installCmds() \
make UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" SEMOD_EXP="/usr/bin/semodule_expand -a" base.pp \
make %{?_smp_mflags} validate UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" SEMOD_EXP="/usr/bin/semodule_expand -a" modules \
make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}  %{separatePkgs}" install \
#make %{?_smp_mflags} UNK_PERMS=%5 NAME=%1 TYPE=%2 DISTRO=%{distro} UBAC=y DIRECT_INITRC=%3 MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} POLY=%4 MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules} %{separatePkgs}" install-appconfig \
#%{__cp} *.pp %{buildroot}/%{_usr}/share/selinux/%1/ \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/policy \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/modules/active \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/contexts/files \
touch %{buildroot}/%{_sysconfdir}/selinux/%1/modules/semanage.read.LOCK \
touch %{buildroot}/%{_sysconfdir}/selinux/%1/modules/semanage.trans.LOCK \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/booleans \
touch %{buildroot}%{_sysconfdir}/selinux/%1/seusers \
touch %{buildroot}%{_sysconfdir}/selinux/%1/policy/policy.%{POLICYVER} \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
touch %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
install -m0644 selinux_config/securetty_types-custom %{buildroot}%{_sysconfdir}/selinux/%1/contexts/securetty_types \
install -m0644 selinux_config/file_contexts.subs_dist %{buildroot}%{_sysconfdir}/selinux/%1/contexts/files \
install -m0644 selinux_config/setrans-custom.conf %{buildroot}%{_sysconfdir}/selinux/%1/setrans.conf \
install -m0644 selinux_config/customizable_types %{buildroot}%{_sysconfdir}/selinux/%1/contexts/customizable_types \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/seusers \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/file_contexts.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/nodes.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/users_extra.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/users.local \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/file_contexts.homedirs.bin \
touch %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/file_contexts.bin \
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/selinux/%1/logins \
find %{buildroot}/%{_usr}/share/selinux/%1/ -type f |xargs -P `/usr/bin/nproc` -n `/usr/bin/nproc`  bzip2 \
for i in %{buildroot}/%{_usr}/share/selinux/%1/*; do mv ${i} ${i%.bz2}; done \
awk '$1 !~ "/^#/" && $2 == "=" && $3 == "module" { printf "%%s.pp ", $1 }' ./policy/modules.conf > %{buildroot}/%{_usr}/share/selinux/%1/modules.lst \
[ x"%{enable_modules}" != "x" ] && for i in %{enable_modules}; do echo ${i}.pp >> %{buildroot}/%{_usr}/share/selinux/%1/modules.lst; done \
SORTED_PKGS=`for p in %{separatePkgs}; do echo $p | awk '{ print length($0) " " $0; }'; done | sort -r -n | cut -d ' ' -f 2` \
for f in ${SORTED_PKGS}; do grep $f\.pp\ %{buildroot}/%{_usr}/share/selinux/%1/modules.lst || (echo "failed to update module.lst for module $f" && exit -1); sed -i -e "s/$f.pp//g" %{buildroot}/%{_usr}/share/selinux/%1/modules.lst; done \
mkdir -p %{buildroot}/%{_sysconfdir}/selinux/%1/modules/active/modules/ \
cp %{buildroot}/%{_usr}/share/selinux/%1/*.pp %{buildroot}/%{_sysconfdir}/selinux/%1/modules/active/modules/ \
rm -f  %{buildroot}/%{_sysconfdir}/selinux/%1/modules/active/modules/base.pp \
cp %{buildroot}/%{_usr}/share/selinux/%1/base.pp %{buildroot}/%{_sysconfdir}/selinux/%1/modules/active/base.pp \
/usr/sbin/semodule -s %1 -n -B -p %{buildroot}; \
/usr/bin/sha512sum %{buildroot}%{_sysconfdir}/selinux/%1/policy/policy.%{POLICYVER} | cut -d' ' -f 1 > %{buildroot}%{_sysconfdir}/selinux/%1/.policy.sha512; \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/contexts/netfilter_contexts  \
rm -rf %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/policy.kern \
ln -sf /etc/selinux/%1/policy/policy.%{POLICYVER}  %{buildroot}%{_sysconfdir}/selinux/%1/modules/active/policy.kern \
rm -rf %{buildroot}/usr/share/selinux/devel/include
%nil

%global excludes() %(for f in %{separatePkgs}; do echo "%exclude %{_usr}/share/selinux/%1/${f}.pp"; done )
 
%define fileList() \
%defattr(-,root,root) \
%dir %{_usr}/share/selinux/%1 \
%dir %{_sysconfdir}/selinux/%1 \
%config(noreplace) %{_sysconfdir}/selinux/%1/setrans.conf \
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/seusers \
%dir %{_sysconfdir}/selinux/%1/logins \
%dir %{_sysconfdir}/selinux/%1/modules \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/semanage.read.LOCK \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/semanage.trans.LOCK \
%dir %attr(700,root,root) %dir %{_sysconfdir}/selinux/%1/modules/active \
%dir %{_sysconfdir}/selinux/%1/modules/active/modules \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/commit_num \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/base.pp \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/modules/*.pp \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/file_contexts \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/file_contexts.homedirs \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/file_contexts.template \
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/seusers.final \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/netfilter_contexts \
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/users_extra \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/homedir_template \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/modules/active/policy.kern \
%ghost %{_sysconfdir}/selinux/%1/modules/active/*.local \
%ghost %{_sysconfdir}/selinux/%1/modules/active/*.bin \
%ghost %{_sysconfdir}/selinux/%1/modules/active/seusers \
%dir %{_sysconfdir}/selinux/%1/policy/ \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/policy/policy.%{POLICYVER} \
%{_sysconfdir}/selinux/%1/.policy.sha512 \
%dir %{_sysconfdir}/selinux/%1/contexts \
%config %{_sysconfdir}/selinux/%1/contexts/customizable_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/securetty_types \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/dbus_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/x_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/default_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/virtual_domain_context \
%config %{_sysconfdir}/selinux/%1/contexts/virtual_image_context \
%config %{_sysconfdir}/selinux/%1/contexts/lxc_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/systemd_contexts \
%config %{_sysconfdir}/selinux/%1/contexts/sepgsql_contexts \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/default_type \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/failsafe_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/initrc_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/removable_context \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/userhelper_context \
%dir %{_sysconfdir}/selinux/%1/contexts/files \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts \
%verify(not md5 size mtime) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.homedirs \
%ghost %{_sysconfdir}/selinux/%1/contexts/files/*.bin \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.local \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs \
%{_sysconfdir}/selinux/%1/contexts/files/file_contexts.subs_dist \
%config %{_sysconfdir}/selinux/%1/contexts/files/media \
%dir %{_sysconfdir}/selinux/%1/contexts/users \
%config(noreplace) %{_sysconfdir}/selinux/%1/contexts/users/* \
%{_mandir}/man*/* \
%{_mandir}/ru/*/* \
%{_usr}/share/selinux/%1/*.pp \
%{_usr}/share/selinux/%1/modules.lst \
%dir %{_usr}/share/selinux/%1/include \
%{_usr}/share/selinux/%1/include/*


%define saveFileContext() \
if [ -s /etc/selinux/config ]; then \
     . %{_sysconfdir}/selinux/config; \
     FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
     if [ "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT} ]; then \
        [ -f ${FILE_CONTEXT}.pre ] || cp -f ${FILE_CONTEXT} ${FILE_CONTEXT}.pre; \
     fi \
fi

#%define loadpolicy() \
#. %{_sysconfdir}/selinux/config; \
#( cd /usr/share/selinux/%1; semodule -n -b base.pp -i %2 -s %1 2>&1 ); \

%define relabel() \
. %{_sysconfdir}/selinux/config; \
FILE_CONTEXT=%{_sysconfdir}/selinux/%1/contexts/files/file_contexts; \
selinuxenabled; \
if [ $? = 0  -a "${SELINUXTYPE}" = %1 -a -f ${FILE_CONTEXT}.pre ]; then \
     fixfiles -C ${FILE_CONTEXT}.pre restore; \
     restorecon -R /root /var/log /var/run 2> /dev/null; \
     rm -f ${FILE_CONTEXT}.pre; \
fi; 

%description
SELinux Reference Policy - modular.

%build

%prep 
%setup -n %{pkgname} -q

%install
%{__rm} -fR %{buildroot}
mkdir -p %{buildroot}%{_mandir}
cp -R  man/* %{buildroot}%{_mandir}
mkdir -p %{buildroot}%{_sysconfdir}/selinux
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
touch %{buildroot}%{_sysconfdir}/selinux/config
touch %{buildroot}%{_sysconfdir}/sysconfig/selinux

# Always create policy module package directories
mkdir -p %{buildroot}%{_usr}/share/selinux/{mcs,mls,modules}/

# Install devel
make %{?_smp_mflags} clean
# installCmds NAME TYPE DIRECT_INITRC POLY UNKNOWN
%installCmds mcs mcs n y deny
%installCmds mls mls n y deny

make %{?_smp_mflags} UNK_PERMS=deny NAME=mcs TYPE=mcs DISTRO=%{distro} UBAC=y DIRECT_INITRC=n MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} PKGNAME=%{name}-%{version} POLY=y MLS_CATS=1024 MCS_CATS=1024 APPS_MODS="%{enable_modules}" install-headers install-docs
cp -R  man/* %{buildroot}%{_mandir}
make UNK_PERMS=allow NAME=mls TYPE=mcs DISTRO=%{distro} UBAC=n DIRECT_INITRC=n MONOLITHIC=%{monolithic} DESTDIR=%{buildroot} PKGNAME=%{name} MLS_CATS=1024 MCS_CATS=1024 install-headers
mkdir %{buildroot}%{_usr}/share/selinux/devel/
mkdir %{buildroot}%{_usr}/share/selinux/packages/
install -m 644 selinux_config/Makefile.devel %{buildroot}%{_usr}/share/selinux/devel/Makefile
install -m 644 doc/example.* %{buildroot}%{_usr}/share/selinux/devel/
install -m 644 doc/policy.* %{buildroot}%{_usr}/share/selinux/devel/
echo  "xdg-open file:///usr/share/doc/selinux-policy/html/index.html"> %{buildroot}%{_usr}/share/selinux/devel/policyhelp
chmod +x %{buildroot}%{_usr}/share/selinux/devel/policyhelp
# This insanity is b/c libselinux always looks at the host's /etc/selinux/config
# and even though you can specify a diff "root" below, it still uses libselinux 
# which means the root is only used for output, it is consulted for the pol
ln -s %{buildroot}/etc/selinux/mcs %{buildroot}/etc/selinux/targeted  
/usr/bin/sepolicy manpage -a -p %{buildroot}/usr/share/man/man8/ -w -r %{buildroot}
rm %{buildroot}/etc/selinux/targeted
mkdir %{buildroot}%{_usr}/share/selinux/devel/html
htmldir=`compgen -d %{buildroot}%{_usr}/share/man/man8/`
mv ${htmldir}/* %{buildroot}%{_usr}/share/selinux/devel/html
mv %{buildroot}%{_usr}/share/man/man8/index.html %{buildroot}%{_usr}/share/selinux/devel/html
mv %{buildroot}%{_usr}/share/man/man8/style.css %{buildroot}%{_usr}/share/selinux/devel/html
rm -rf ${htmldir}
chmod +x %{buildroot}%{_usr}/share/selinux/devel/policyhelp
%clean
%{__rm} -fR %{buildroot}

%post
if [ ! -e /etc/selinux/config ]; then
#
#     New install so we will default to selinux-policy policy
#
echo "
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=%{enforcing_mode}
# SELINUXTYPE= can take one of these two values:
#     mcs - standard Multi Category security policy,
#     mls - Multi Level Security security policy.
SELINUXTYPE=mcs

" > /etc/selinux/config
fi

sed -e 's/^SELINUXTYPE=.*/SELINUXTYPE=mcs/' -i /etc/selinux/config

ln -sf /etc/selinux/config /etc/sysconfig/selinux 
restorecon /etc/selinux/config 2> /dev/null || :

exit 0

%postun
if [ $1 = 0 ]; then
     setenforce 0 2> /dev/null
     if [ ! -s /etc/selinux/config ]; then
          echo "SELINUX=disabled" > /etc/selinux/config
     else
          sed -i 's/^SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config
     fi
fi
exit 0

%package mcs
Summary: SELinux selinux-policy base policy
Provides: selinux-policy-base = %{version}-%{release}
Group: System Environment/Base
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Conflicts:  audispd-plugins <= 1.7.7-1
Conflicts:  seedit
Obsoletes: selinux-policy-targeted, selinux-policy-minimum, selinux-policy-mls 

%description mcs 
MCS policy

%pre mcs
%saveFileContext mcs

%post mcs
sed -e 's/^SELINUXTYPE=.*/SELINUXTYPE=mcs/' -i /etc/selinux/config
# if first time update booleans.local needs to be copied to sandbox
[ -f /etc/selinux/mcs/booleans.local ] && mv /etc/selinux/mcs/booleans.local /etc/selinux/mcs/modules/active/
[ -f /etc/selinux/mcs/seusers ] && cp -f /etc/selinux/mcs/seusers /etc/selinux/mcs/modules/active/seusers

packages=`cat /usr/share/selinux/mcs/modules.lst`
if [ $1 -eq 1 ]; then
   #%loadpolicy mcs $packages
   semodule -R
   restorecon -R /root /var/log /var/run 2> /dev/null
else
#   semodule -n -s mcs 2>/dev/null
   #%loadpolicy mcs $packages
   %relabel mcs
fi
touch /.autorelabel
rm -f /usr/share/selinux/devel/include
ln -s /usr/share/selinux/mcs/include /usr/share/selinux/devel
exit 0

%files mcs 
%defattr(-,root,root,-)
%fileList mcs

%excludes mcs

%package mls 
Summary: SELinux mls base policy
Group: System Environment/Base
Provides: selinux-policy-base = %{version}-%{release}
Requires: policycoreutils-newrole >= %{POLICYCOREUTILSVER} setransd
Requires(pre): policycoreutils >= %{POLICYCOREUTILSVER}
Requires(pre): coreutils
Requires(pre): selinux-policy = %{version}-%{release}
Requires: selinux-policy = %{version}-%{release}
Conflicts:  seedit
Obsoletes: selinux-policy-targeted, selinux-policy-minimum, selinux-policy-mls 

%description mls 
Stabdard MLS policy

%pre mls 
%saveFileContext mls

%post mls 
sed -e 's/^SELINUXTYPE=.*/SELINUXTYPE=mls/' -i /etc/selinux/config
# if first time update booleans.local needs to be copied to sandbox
[ -f /etc/selinux/mls/booleans.local ] && mv /etc/selinux/mls/booleans.local /etc/selinux/mls/modules/active/
[ -f /etc/selinux/mls/seusers ] && cp -f /etc/selinux/mls/seusers /etc/selinux/mls/modules/active/seusers
#semodule -n -s mls 2>/dev/null
#packages=`cat /usr/share/selinux/mls/modules.lst`
#%loadpolicy mls $packages
semodule -R
rm -f /usr/share/selinux/devel/include
ln -s /usr/share/selinux/mls/include /usr/share/selinux/devel

if [ $1 -eq 1 ]; then
   restorecon -R /root /var/log /var/run 2> /dev/null
else
%relabel mls
fi
exit 0

%files mls
%defattr(-,root,root,-)
%fileList mls

%excludes  mls


%changelog
