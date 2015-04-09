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
mkdir -p $RPM_BUILD_ROOT/usr/share/clip-miscfiles/old
mkdir -p $RPM_BUILD_ROOT/usr/share/clip-miscfiles/new
cp -a * $RPM_BUILD_ROOT/usr/share/clip-miscfiles/new

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/usr/share/clip-miscfiles/*

%post
cd /usr/share/clip-miscfiles/new
# First, make a backup of all files that exist already.
for f in `find . -type f`; do
	[ -e /${f} ] && ( mkdir -p /usr/share/clip-miscfiles/old/$(dirname ${f}); cp /${f} /usr/share/clip-miscfiles/old/$(dirname ${f}))
done
# Copy our content to /
cp -a /usr/share/clip-miscfiles/new/* /

%preun
cd /usr/share/clip-miscfiles/old
# First, remove all of the files that didn't exist in the first place
for f in `find . -type f`; do
	[ ! -e /${f} ] && rm -f /${f}
done
# Now restore our original backups of files that did exist.
cp -a /usr/share/clip-miscfiles/new/old /


%changelog
* Mon Aug 26 2014 Spencer Shimko <spencer@quarksecurity.com> 1-1
- Initial support for miscfiles.
