Name:	anaconda-dracut
Version: 21.48.22.56
Release: 5
Summary: Anaconda's Dracut module
Requires: anaconda, dracut

License: GPL or BSD
Group: System Environment/Base

BuildRequires: make, coreutils
BuildRoot: %{_tmppath}/%{name}-root

Source0: %{pkgname}-%{version}.tgz

%description
This module contains the files extracted
from Anaconda's dracut module so we
can use it when rolling initrd

%prep
%setup -q -n %{pkgname}

%build

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(755,root,root,-)
/usr/lib/dracut/modules.d/80anaconda/*


%post

%changelog
* Fri Jun 03 2016 Spencer Shimko <spencer@quarksecurity.com> 1-1
- Inital import of Anaconda's dracut module.

