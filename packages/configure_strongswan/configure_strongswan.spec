Name:	%{pkgname}
Version: %{version}
Release: %{release}
Summary: Strongswan configuration utilities.
Requires: kernel

License: GPL or BSD
Group: System Environment/Base

BuildRequires: make, bash
BuildRoot: %{_tmppath}/%{name}-root

Source0: %{pkgname}-%{version}.tgz

%description
This package contains utilities for configuring strongswan

%prep
%setup -q -n %{pkgname}

%build
make

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=%{buildroot} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(6755,root,root,-)
/usr/bin/add_ss_user
%defattr(755,root,root,-)
/etc/init.d/configure-strongswan
/usr/bin/add_vpn_user.sh
/usr/bin/gen_passwd.sh
/usr/bin/gen_subj.sh
/usr/bin/gen_word.sh
/usr/bin/strongswan_login.py

%post

%changelog
* Tue Apr 21 2014 Pat McClory <pat@quarksecurity.com> 1-1
- Configure strongswan Spec file
