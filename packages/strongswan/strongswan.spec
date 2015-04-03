%global _hardened_build 1
# When packaging pre-release snapshots:
# 1) Please use 0.x in the release to maintain the correct package version
# order.
# 2) Please use the following define (with a percent sign and the appropriate
# prerelease tag):
#     define prerelease dr6

Name:           strongswan
Version:        5.2.0
Release:        7%{?prerelease:.%{prerelease}}%{?dist}
Summary:        An OpenSource IPsec-based VPN and TNC solution
Group:          System Environment/Daemons
License:        GPLv2+
URL:            http://www.strongswan.org/
Source0:        http://download.strongswan.org/%{name}-%{version}%{?prerelease}.tar.bz2
# Initscript for epel6
Source1:        %{name}.sysvinit
Patch0:         strongswan-5.2.0-json.patch
Patch1:         fix_updown.patch

# Use RTLD_GLOBAL when loading plugins and link them to libstrongswan
#
# The patch hasn't been accepted upstream because of insufficient
# information from the author. This situation needs to be fixed or
# the patch needs to be removed to avoid diverging from upstream
# permanently.
#
# http://wiki.strongswan.org/issues/538
#
# Removing the patch from the build as I repeatedly requested that it should be
# upstreamed. No comment has been added to the upstream bug report. Nothing
# has been done towards the goal of upstreaming the patch.
#
# See also:
#
#  * https://bugzilla.redhat.com/show_bug.cgi?id=1087437
#  * http://fedoraproject.org/wiki/Packaging:Guidelines#All_patches_should_have_an_upstream_bug_link_or_comment
#  * https://fedoraproject.org/wiki/Staying_close_to_upstream_projects
#
# The patches violated the packaging guidelines from the beginning so I took
# the initiative to merge them and submit them upstream. But I couldn't work
# with the upstream developers on the fix as I didn't have enough information
# about the use cases. Please cooperate with usptream and get the patch
# accepted. There's nothing Fedora specific in the patch.
#
#Patch1:         strongswan-5.1.1-plugins.patch
BuildRequires:  gmp-devel autoconf automake
BuildRequires:  libcurl-devel
BuildRequires:  openldap-devel
BuildRequires:  openssl-devel
BuildRequires:  sqlite-devel
BuildRequires:  gettext-devel
BuildRequires:  trousers-devel
BuildRequires:  libxml2-devel
BuildRequires:  pam-devel
BuildRequires:  json-c-devel
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
BuildRequires:  NetworkManager-devel
BuildRequires:  NetworkManager-glib-devel
Obsoletes:      %{name}-NetworkManager < 0:5.0.4-5
BuildRequires:  systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Obsoletes:      %{name}-NetworkManager < 0:5.0.0-3.git20120619
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

%define _binaries_in_noarch_packages_terminate_build 0

%description
The strongSwan IPsec implementation supports both the IKEv1 and IKEv2 key
exchange protocols in conjunction with the native NETKEY IPsec stack of the
Linux kernel.

%package libipsec
Summary: Strongswan's libipsec backend
Group: System Environment/Daemons
%description libipsec
The kernel-libipsec plugin provides an IPsec backend that works entirely
in userland, using TUN devices and its own IPsec implementation libipsec.

%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%package charon-nm
Summary:        NetworkManager plugin for Strongswan
Group:          System Environment/Daemons
%description charon-nm
NetworkManager plugin integrates a subset of Strongswan capabilities
to NetworkManager.
%endif

%package tnc-imcvs
Summary: Trusted network connect (TNC)'s IMC/IMV functionality
Group: Applications/System
Requires: %{name} = %{version}
%description tnc-imcvs
This package provides Trusted Network Connect's (TNC) architecture support.
It includes support for TNC client and server (IF-TNCCS), IMC and IMV message
exchange (IF-M), interface between IMC/IMV and TNC client/server (IF-IMC
and IF-IMV). It also includes PTS based IMC/IMV for TPM based remote
attestation, SWID IMC/IMV, and OS IMC/IMV. It's IMC/IMV dynamic libraries
modules can be used by any third party TNC Client/Server implementation
possessing a standard IF-IMC/IMV interface. In addition, it implements
PT-TLS to support TNC over TLS.

%prep
%setup -q -n %{name}-%{version}%{?prerelease}
%patch0 -p1
%patch1 -p1
#%patch1 -p1

echo "For migration from 4.6 to 5.0 see http://wiki.strongswan.org/projects/strongswan/wiki/CharonPlutoIKEv1" > README.Fedora

%build
autoreconf
# --with-ipsecdir moves internal commands to /usr/libexec/strongswan
# --bindir moves 'pki' command to /usr/libexec/strongswan
# See: http://wiki.strongswan.org/issues/552
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/lib64/pkgconfig
%configure --disable-static \
    --with-ipsec-script=%{name} \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --with-ipsecdir=%{_libexecdir}/%{name} \
    --bindir=%{_libexecdir}/%{name} \
    --with-ipseclibdir=%{_libdir}/%{name} \
    --with-fips-mode=2 \
    --with-tss=trousers \
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
    --enable-nm \
%endif
    --enable-openssl \
    --enable-md4 \
    --enable-xauth-eap \
    --enable-xauth-pam \
    --enable-xauth-noauth \
    --enable-eap-md5 \
    --enable-eap-gtc \
    --enable-eap-tls \
    --enable-eap-ttls \
    --enable-eap-peap \
    --enable-eap-mschapv2 \
    --enable-farp \
    --enable-dhcp \
    --enable-sqlite \
    --enable-tnc-ifmap \
    --enable-tnc-pdp \
    --enable-imc-test \
    --enable-imv-test \
    --enable-imc-scanner \
    --enable-imv-scanner  \
    --enable-imc-attestation \
    --enable-imv-attestation \
    --enable-imv-os \
    --enable-imc-os \
    --enable-imc-swid \
    --enable-imv-swid \
    --enable-eap-tnc \
    --enable-tnccs-20 \
    --enable-tnccs-11 \
    --enable-tnccs-dynamic \
    --enable-tnc-imc \
    --enable-tnc-imv \
    --enable-eap-radius \
    --enable-curl \
    --enable-eap-identity \
    --enable-cmd \
    --enable-acert \
    --enable-aikgen \
    --enable-vici \
    --enable-swanctl \
    --enable-kernel-libipsec

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
# prefix man pages
for i in %{buildroot}%{_mandir}/*/*; do
    if echo "$i" | grep -vq '/%{name}[^\/]*$'; then
        mv "$i" "`echo "$i" | sed -re 's|/([^/]+)$|/%{name}_\1|'`"
    fi
done
# delete unwanted library files
rm %{buildroot}%{_libdir}/%{name}/*.so
find %{buildroot} -type f -name '*.la' -delete
# fix config permissions
chmod 644 %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
# protect configuration from ordinary user's eyes
chmod 700 %{buildroot}%{_sysconfdir}/%{name}
# Create ipsec.d directory tree.
install -d -m 700 %{buildroot}%{_sysconfdir}/%{name}/ipsec.d
for i in aacerts acerts certs cacerts crls ocspcerts private reqs; do
    install -d -m 700 %{buildroot}%{_sysconfdir}/%{name}/ipsec.d/${i}
done

%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%else
install -D -m 755 %{SOURCE1} %{buildroot}/%{_initddir}/%{name}
%endif

%post
/sbin/ldconfig
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%systemd_post %{name}.service
%else
/sbin/chkconfig --add %{name}
%endif

%preun
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%systemd_preun %{name}.service
%else
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
%endif

%postun
/sbin/ldconfig
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%systemd_postun_with_restart %{name}.service
%else
%endif

%files
%doc README README.Fedora COPYING NEWS TODO
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/%{name}/ipsec.d/
%config(noreplace) %{_sysconfdir}/%{name}/ipsec.conf
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%dir %{_sysconfdir}/%{name}/swanctl/
%config(noreplace) %{_sysconfdir}/%{name}/swanctl/swanctl.conf
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%{_unitdir}/%{name}.service
%else
%{_initddir}/%{name}
%endif
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libcharon.so.0
%{_libdir}/%{name}/libcharon.so.0.0.0
%{_libdir}/%{name}/libhydra.so.0
%{_libdir}/%{name}/libhydra.so.0.0.0
%{_libdir}/%{name}/libtls.so.0
%{_libdir}/%{name}/libtls.so.0.0.0
%{_libdir}/%{name}/libpttls.so.0
%{_libdir}/%{name}/libpttls.so.0.0.0
%{_libdir}/%{name}/lib%{name}.so.0
%{_libdir}/%{name}/lib%{name}.so.0.0.0
%{_libdir}/%{name}/libvici.so.0
%{_libdir}/%{name}/libvici.so.0.0.0
%dir %{_libdir}/%{name}/plugins
%{_libdir}/%{name}/plugins/lib%{name}-aes.so
%{_libdir}/%{name}/plugins/lib%{name}-attr.so
%{_libdir}/%{name}/plugins/lib%{name}-cmac.so
%{_libdir}/%{name}/plugins/lib%{name}-constraints.so
%{_libdir}/%{name}/plugins/lib%{name}-des.so
%{_libdir}/%{name}/plugins/lib%{name}-dnskey.so
%{_libdir}/%{name}/plugins/lib%{name}-fips-prf.so
%{_libdir}/%{name}/plugins/lib%{name}-gmp.so
%{_libdir}/%{name}/plugins/lib%{name}-hmac.so
%{_libdir}/%{name}/plugins/lib%{name}-kernel-netlink.so
%{_libdir}/%{name}/plugins/lib%{name}-md5.so
%{_libdir}/%{name}/plugins/lib%{name}-nonce.so
%{_libdir}/%{name}/plugins/lib%{name}-openssl.so
%{_libdir}/%{name}/plugins/lib%{name}-pem.so
%{_libdir}/%{name}/plugins/lib%{name}-pgp.so
%{_libdir}/%{name}/plugins/lib%{name}-pkcs1.so
%{_libdir}/%{name}/plugins/lib%{name}-pkcs8.so
%{_libdir}/%{name}/plugins/lib%{name}-pkcs12.so
%{_libdir}/%{name}/plugins/lib%{name}-rc2.so
%{_libdir}/%{name}/plugins/lib%{name}-sshkey.so
%{_libdir}/%{name}/plugins/lib%{name}-pubkey.so
%{_libdir}/%{name}/plugins/lib%{name}-random.so
%{_libdir}/%{name}/plugins/lib%{name}-resolve.so
%{_libdir}/%{name}/plugins/lib%{name}-revocation.so
%{_libdir}/%{name}/plugins/lib%{name}-sha1.so
%{_libdir}/%{name}/plugins/lib%{name}-sha2.so
%{_libdir}/%{name}/plugins/lib%{name}-socket-default.so
%{_libdir}/%{name}/plugins/lib%{name}-stroke.so
%{_libdir}/%{name}/plugins/lib%{name}-updown.so
%{_libdir}/%{name}/plugins/lib%{name}-x509.so
%{_libdir}/%{name}/plugins/lib%{name}-xauth-generic.so
%{_libdir}/%{name}/plugins/lib%{name}-xauth-eap.so
%{_libdir}/%{name}/plugins/lib%{name}-xauth-pam.so
%{_libdir}/%{name}/plugins/lib%{name}-xauth-noauth.so
%{_libdir}/%{name}/plugins/lib%{name}-xcbc.so
%{_libdir}/%{name}/plugins/lib%{name}-md4.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-md5.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-gtc.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-tls.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-ttls.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-peap.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-mschapv2.so
%{_libdir}/%{name}/plugins/lib%{name}-farp.so
%{_libdir}/%{name}/plugins/lib%{name}-dhcp.so
%{_libdir}/%{name}/plugins/lib%{name}-curl.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-identity.so
%{_libdir}/%{name}/plugins/lib%{name}-acert.so
%{_libdir}/%{name}/plugins/lib%{name}-vici.so
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/_copyright
%{_libexecdir}/%{name}/_updown
%{_libexecdir}/%{name}/_updown_espmark
%{_libexecdir}/%{name}/charon
%{_libexecdir}/%{name}/scepclient
%{_libexecdir}/%{name}/starter
%{_libexecdir}/%{name}/stroke
%{_libexecdir}/%{name}/_imv_policy
%{_libexecdir}/%{name}/imv_policy_manager
%{_libexecdir}/%{name}/pki
%{_libexecdir}/%{name}/aikgen
%{_sbindir}/charon-cmd
%{_sbindir}/%{name}
%{_sbindir}/swanctl
%{_mandir}/man1/%{name}_pki*.1.gz
%{_mandir}/man5/%{name}.conf.5.gz
%{_mandir}/man5/%{name}_ipsec.conf.5.gz
%{_mandir}/man5/%{name}_ipsec.secrets.5.gz
%{_mandir}/man5/%{name}_swanctl.conf.5.gz
%{_mandir}/man8/%{name}.8.gz
%{_mandir}/man8/%{name}__updown.8.gz
%{_mandir}/man8/%{name}__updown_espmark.8.gz
%{_mandir}/man8/%{name}_scepclient.8.gz
%{_mandir}/man8/%{name}_charon-cmd.8.gz
%{_mandir}/man8/%{name}_swanctl.8.gz
%{_sysconfdir}/%{name}/%{name}.d/
%{_datadir}/%{name}/templates/config/
%{_datadir}/%{name}/templates/database/
%exclude /usr/lib/debug
%exclude /usr/src/debug

%files tnc-imcvs
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libimcv.so.0
%{_libdir}/%{name}/libimcv.so.0.0.0
%{_libdir}/%{name}/libpts.so.0
%{_libdir}/%{name}/libpts.so.0.0.0
%{_libdir}/%{name}/libtnccs.so.0
%{_libdir}/%{name}/libtnccs.so.0.0.0
%{_libdir}/%{name}/libradius.so.0
%{_libdir}/%{name}/libradius.so.0.0.0
%dir %{_libdir}/%{name}/imcvs
%{_libdir}/%{name}/imcvs/imc-attestation.so
%{_libdir}/%{name}/imcvs/imc-scanner.so
%{_libdir}/%{name}/imcvs/imc-test.so
%{_libdir}/%{name}/imcvs/imc-os.so
%{_libdir}/%{name}/imcvs/imc-swid.so
%{_libdir}/%{name}/imcvs/imv-attestation.so
%{_libdir}/%{name}/imcvs/imv-scanner.so
%{_libdir}/%{name}/imcvs/imv-test.so
%{_libdir}/%{name}/imcvs/imv-os.so
%{_libdir}/%{name}/imcvs/imv-swid.so
%dir %{_libdir}/%{name}/plugins
%{_libdir}/%{name}/plugins/lib%{name}-pkcs7.so
%{_libdir}/%{name}/plugins/lib%{name}-sqlite.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-tnc.so
%{_libdir}/%{name}/plugins/lib%{name}-tnc-imc.so
%{_libdir}/%{name}/plugins/lib%{name}-tnc-imv.so
%{_libdir}/%{name}/plugins/lib%{name}-tnc-tnccs.so
%{_libdir}/%{name}/plugins/lib%{name}-tnccs-20.so
%{_libdir}/%{name}/plugins/lib%{name}-tnccs-11.so
%{_libdir}/%{name}/plugins/lib%{name}-tnccs-dynamic.so
%{_libdir}/%{name}/plugins/lib%{name}-eap-radius.so
%{_libdir}/%{name}/plugins/lib%{name}-tnc-ifmap.so
%{_libdir}/%{name}/plugins/lib%{name}-tnc-pdp.so
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/attest
%{_libexecdir}/%{name}/pacman
%{_libexecdir}/%{name}/pt-tls-client
#swid files
%{_libexecdir}/%{name}/*.swidtag
%dir %{_datadir}/regid.2004-03.org.%{name}
%{_datadir}/regid.2004-03.org.%{name}/*.swidtag

%files libipsec
%{_libdir}/%{name}/libipsec.so.0
%{_libdir}/%{name}/libipsec.so.0.0.0
%{_libdir}/%{name}/plugins/libstrongswan-kernel-libipsec.so

%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%files charon-nm
%doc COPYING
%{_libexecdir}/%{name}/charon-nm
%endif

%changelog
* Tue Feb 17 2015 Pat McClory <pat@quarksecurity.com> - 5.2.0-8
- set pkg_config_path
- Remove /usr/lib/debug

* Thu Sep 25 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-7
- use upstream patch for json/json-c dependency

* Thu Sep 25 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-6
- Resolves: #1146145 - Strongswan is compiled without xauth-noauth plugin

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.2.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Aug 05 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-4
- Resolves: #1081804 - enable Kernel IPSec support

* Wed Jul 30 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-3
- rebuilt

* Tue Jul 29 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-2
- fix json-c dependency

* Tue Jul 15 2014 Avesh Agarwal <avagarwa@redhat.com> - 5.2.0-1
- New upstream release 5.2.0
- The Attestation IMC/IMV pair supports the IMA-NG
  measurement format
- Aikgen tool to generate an Attestation Identity Key bound
  to a TPM
- Swanctl tool to provide a portable, complete IKE
  configuration and control interface for the command
  line using vici interface with libvici library
- PT-EAP transport protocol (RFC 7171) for TNC
- Enabled support for acert for checking X509 attribute certificate
- Updated patches, removed selinux patch as upstream has fixed it
  in this release.
- Updated spec file with minor cleanups

* Thu Jun 26 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-0.4.dr6
- improve prerelease macro

* Thu Jun 26 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-0.3
- Resolves: #1111895 - bump to 5.2.0dr6

* Thu Jun 12 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-0.2
- Related: #1087437 - remove or upstream all patches not specific to fedora/epel

* Thu Jun 12 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0-0.1.dr5
- fix the pre-release version according to guidelines before it gets branched

* Fri Jun 06 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0dr5-1
- new version 5.2.0dr5
- add json-c-devel to build deps

* Mon May 26 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0dr4-3
- merge two related patches

* Mon May 26 2014 Pavel Šimerda <psimerda@redhat.com> - 5.2.0dr4-2
- clean up the patches a bit

* Thu May 22 2014 Avesh Agarwal <avagarwa@redhat.com> - 5.2.0dr4-1
- New upstream developer release 5.2.0dr4
- Attestation IMV/IMC supports IMA-NG measurement format now
- Aikgen tool to generate an Attestation Identity Key bound
  to a TPM
- PT-EAP transport protocol (RFC 7171) for TNC
- vici plugin provides IKE Configuration Interface for charon
- Enabled support for acert for checking X509 attribute certificate
- Updated patches
- Updated spec file with minor cleanups

* Tue Apr 15 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.3-1
- new version 5.1.3

* Mon Apr 14 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.3rc1-1
- new version 5.1.3rc1

* Mon Mar 24 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.2-4
- #1069928 - updated libexec patch.

* Tue Mar 18 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.2-3
- fixed el6 initscript
- fixed pki directory location

* Fri Mar 14 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.2-2
- clean up the specfile a bit
- replace the initscript patch with an individual initscript
- patch to build for epel6

* Mon Mar 03 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.2-1
- #1071353 - bump to 5.1.2
- #1071338 - strongswan is compiled without xauth-pam plugin
- remove obsolete patches
- sent all patches upstream
- added comments to all patches
- don't touch the config with sed

* Thu Feb 20 2014 Avesh Agarwal <avagarwa@redhat.com> - 5.1.1-6
- Fixed full hardening for strongswan (full relro and PIE).
  The previous macros had a typo and did not work
  (see bz#1067119).
- Fixed tnc package description to reflect the current state of
  the package.
- Fixed pki binary and moved it to /usr/libexece/strongswan as
  others binaries are there too.

* Wed Feb 19 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.1-5
- #903638 - SELinux is preventing /usr/sbin/xtables-multi from 'read' accesses on the chr_file /dev/random

* Thu Jan 09 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.1-4
- Removed redundant patches and *.spec commands caused by branch merging

* Wed Jan 08 2014 Pavel Šimerda <psimerda@redhat.com> - 5.1.1-3
- rebuilt

* Mon Dec 2 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.1.1-2
- Resolves: 973315
- Resolves: 1036844

* Fri Nov 1 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.1.1-1
- Support for PT-TLS  (RFC 6876)
- Support for SWID IMC/IMV
- Support for command line IKE client charon-cmd
- Changed location of pki to /usr/bin
- Added swid tags files
- Added man pages for pki and charon-cmd
- Renamed pki to strongswan-pki to avoid conflict with
  pki-core/pki-tools package.
- Update local patches
- Fixes CVE-2013-6075
- Fixes CVE-2013-6076
- Fixed autoconf/automake issue as configure.ac got changed
  and it required running autoreconf during the build process.
- added strongswan signature file to the sources.

* Thu Sep 12 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.1.0-3
- Fixed initialization crash of IMV and IMC particularly
  attestation imv/imc as libstrongswas was not getting
  initialized.

* Fri Aug 30 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.1.0-2
- Enabled fips support
- Enabled TNC's ifmap support
- Enabled TNC's pdp support
- Fixed hardocded package name in this spec file

* Wed Aug 7 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.1.0-1
- rhbz#981429: New upstream release
- Fixes CVE-2013-5018: rhbz#991216, rhbz#991215
- Fixes rhbz#991859 failed to build in rawhide
- Updated local patches and removed which are not needed
- Fixed errors around charon-nm
- Added plugins libstrongswan-pkcs12.so, libstrongswan-rc2.so,
  libstrongswan-sshkey.so
- Added utility imv_policy_manager

* Thu Jul 25 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 5.0.4-5
- rename strongswan-NetworkManager to strongswan-charon-nm
- fix enable_nm macro

* Mon Jul 15 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 5.0.4-4
- %%files tries to package some of the shared objects as directories (#984437)
- fix broken systemd unit file (#984300)
- fix rpmlint error: description-line-too-long
- fix rpmlint error: macro-in-comment
- fix rpmlint error: spelling-error Summary(en_US) fuctionality
- depend on 'systemd' instead of 'systemd-units'
- use new systemd scriptlet macros
- NetworkManager subpackage should have a copy of the license (#984490)
- enable hardened_build as this package meets the PIE criteria (#984429)
- invocation of "ipsec _updown iptables" is broken as ipsec is renamed
  to strongswan in this package (#948306)
- invocation of "ipsec scepclient" is broken as ipsec is renamed
  to strongswan in this package
- add /etc/strongswan/ipsec.d and missing subdirectories
- conditionalize building of strongswan-NetworkManager subpackage as the
  version of NetworkManager in EL6 is too old (#984497)

* Fri Jun 28 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.0.4-3
- Patch to fix a major crash issue when Freeradius loads
  attestatiom-imv and does not initialize libstrongswan which
  causes crash due to calls to PTS algorithms probing APIs.
  So this patch fixes the order of initialization. This issues
  does not occur with charon because libstrongswan gets
  initialized earlier.
- Patch that allows to outputs errors when there are permission
  issues when accessing strongswan.conf.
- Patch to make loading of modules configurable when libimcv
  is used in stand alone mode without charon with freeradius
  and wpa_supplicant.

* Tue Jun 11 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.0.4-2
- Enabled TNCCS 1.1 protocol
- Fixed libxm2-devel build dependency
- Patch to fix the issue with loading of plugins

* Wed May 1 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.0.4-1
- New upstream release
- Fixes for CVE-2013-2944
- Enabled support for OS IMV/IMC
- Created and applied a patch to disable ECP in fedora, because
  Openssl in Fedora does not allow ECP_256 and ECP_384. It makes
  it non-compliant to TCG's PTS standard, but there is no choice
  right now. see redhat bz # 319901.
- Enabled Trousers support for TPM based operations.

* Sat Apr 20 2013 Pavel Šimerda <psimerda@redhat.com> - 5.0.3-2
- Rebuilt for a single specfile for rawhide/f19/f18/el6

* Fri Apr 19 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.0.3-1
- New upstream release
- Enabled curl and eap-identity plugins
- Enabled support for eap-radius plugin.

* Thu Apr 18 2013 Pavel Šimerda <psimerda@redhat.com> - 5.0.2-3
- Add gettext-devel to BuildRequires because of epel6
- Remove unnecessary comments

* Tue Mar 19 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.0.2-2
- Enabled support for eap-radius plugin.

* Mon Mar 11 2013 Avesh Agarwal <avagarwa@redhat.com> - 5.0.2-1
- Update to upstream release 5.0.2
- Created sub package strongswan-tnc-imcvs that provides trusted network
  connect's IMC and IMV funtionality. Specifically it includes PTS 
  based IMC/IMV for TPM based remote attestation and scanner and test 
  IMCs and IMVs. The Strongswan's IMC/IMV dynamic libraries can be used 
  by any third party TNC Client/Server implementation possessing a 
  standard IF-IMC/IMV interface.

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Oct 04 2012 Pavel Šimerda <psimerda@redhat.com> - 5.0.1-1
- Update to release 5.0.1

* Thu Oct 04 2012 Pavel Šimerda <psimerda@redhat.com> - 5.0.0-4.git20120619
- Add plugins to interoperate with Windows 7 and Android (#862472)
  (contributed by Haim Gelfenbeyn)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.0.0-3.git20120619
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jul 08 2012 Pavel Šimerda <pavlix@pavlix.net> - 5.0.0-2.git20120619
- Fix configure substitutions in initscripts

* Wed Jul 04 2012 Pavel Šimerda <psimerda@redhat.com> - 5.0.0-1.git20120619
- Update to current upstream release
- Comment out all stuff that is only needed for git builds
- Remove renaming patch from git
- Improve init patch used for EPEL

* Thu Jun 21 2012 Pavel Šimerda <psimerda@redhat.com> - 5.0.0-0.3.git20120619
- Build with openssl plugin enabled

* Wed Jun 20 2012 Pavel Šimerda <psimerda@redhat.com> - 5.0.0-0.2.git20120619
- Add README.Fedora with link to 4.6 to 5.0 migration information

* Tue Jun 19 2012 Pavel Šimerda - 5.0.0-0.1.git20120619
- Snapshot of upcoming major release
- Move patches and renaming upstream
  http://wiki.strongswan.org/issues/194
  http://wiki.strongswan.org/issues/195
- Notified upstream about manpage issues

* Tue Jun 19 2012 Pavel Šimerda - 4.6.4-2
- Make initscript patch more distro-neutral
- Add links to bugreports for patches

* Fri Jun 01 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.4-1
- New upstream version (CVE-2012-2388)

* Sat May 26 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.3-2
- Add --enable-nm to configure
- Add NetworkManager-devel to BuildRequires
- Add NetworkManager-glib-devel to BuildRequires
- Add strongswan-NetworkManager package

* Sat May 26 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.3-1
- New version of Strongswan
- Support for RFC 3110 DNSKEY (see upstream changelog)
- Fix corrupt scriptlets

* Fri Mar 30 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.2-2
- #808612 - strongswan binary renaming side-effect

* Sun Feb 26 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.2-1
- New upstream version
- Changed from .tar.gz to .tar.bz2
- Added libstrongswan-pkcs8.so

* Wed Feb 15 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-8
- Fix initscript's status function

* Wed Feb 15 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-7
- Expand tabs in config files for better readability
- Add sysvinit script for epel6

* Wed Feb 15 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-6
- Fix program name in systemd unit file

* Tue Feb 14 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-5
- Improve fedora/epel conditionals

* Sat Jan 21 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-4
- Protect configuration directory from ordinary users
- Add still missing directory /etc/strongswan

* Fri Jan 20 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-3
- Change directory structure to avoid clashes with Openswan
- Prefixed all manpages with 'strongswan_'
- Every file now includes 'strongswan' somewhere in its path
- Removed conflict with Openswan
- Finally fix permissions on strongswan.conf

* Fri Jan 20 2012 Pavel Šimerda <pavlix@pavlix.net> - 4.6.1-2
- Change license tag from GPL to GPLv2+
- Change permissions on /etc/strongswan.conf to 644
- Rename ipsec.8 manpage to strongswan.8
- Fix empty scriptlets for non-fedora builds
- Add ldconfig scriptlet
- Add missing directories and files

* Sun Jan 01 2012 Pavel Šimerda <pavlix@pavlix.net - 4.6.1-1
- Bump to version 4.6.1

* Sun Jan 01 2012 Pavel Šimerda <pavlix@pavlix.net - 4.6.0-3
- Add systemd scriptlets
- Add conditions to also support EPEL6

* Sat Dec 10 2011 Pavel Šimerda <pavlix@pavlix.net> - 4.6.0-2
- Experimental build for development
