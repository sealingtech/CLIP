Name:	%{pkgname}
Version: %{version}
Release: %{release}
Summary: Miscellaneous files from CLIP.
Requires: rootfiles

License: GPL or BSD
Group: System Environment/Base

BuildRequires: coreutils
BuildRoot: %{_tmppath}/%{name}-root

Source0: %{pkgname}-%{version}.tgz

%description
This package is a stub, end-users add content
to packages/clip-miscfiles/clip-miscfiles and 
they will be copied into the deployed 
environment.

An example are those that still rely
on tarballs for deployment.  Instead,
drop the files in the directory listed
above and they will be included in this
package.


%prep
%setup -q -n %{pkgname}

%build

%install
mkdir -p $RPM_BUILD_ROOT/usr/share/clip-miscfiles/root
cp -a * $RPM_BUILD_ROOT/usr/share/clip-miscfiles/root

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/usr/share/clip-miscfiles/*

%post
#TODO: this should create a db of hashes and original files and on uninstall
# removal of this package it should restore files that 
# haven't been modified in the interim.
cp -a /usr/share/clip-miscfiles/root/* /


%changelog
* Mon Aug 26 2014 Spencer Shimko <spencer@quarksecurity.com> 1-1
- Initial support for miscfiles.
