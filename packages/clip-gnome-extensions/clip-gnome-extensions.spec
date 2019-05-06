Name:	clip-gnome-extensions
Version: 1
Release: 1
Summary: CLIP package for gnome extensions.
License: GPL or BSD
Group: System Environment/Base
Requires: gnome-shell
Requires: dconf
BuildRoot: %{_tmppath}/%{name}-root
Source0: %{pkgname}-%{version}.tgz

%description
A package containing gnome extensions.

%prep
%setup -q -n %{pkgname}

%build

%install
mkdir -p $RPM_BUILD_ROOT/usr/share/gnome-shell/extensions/
mkdir -p $RPM_BUILD_ROOT/etc/dconf/db/local.d/
mkdir -p $RPM_BUILD_ROOT/etc/dconf/db/local.d/locks/
cp -r disable_account_settings@clip.quarksecurity.com $RPM_BUILD_ROOT/usr/share/gnome-shell/extensions
cp extensions-dconf $RPM_BUILD_ROOT/etc/dconf/db/local.d/00-extensions
#echo "/org/gnome/shell/enabled-extensions" > $RPM_BUILD_ROOT/etc/dconf/db/local.d/locks/extensions

%clean

%files
%defattr(0444,root,root,0555)
#%attr(0444,root,root) /etc/dconf/db/local.d/locks/extensions
/etc/dconf/db/local.d/00-extensions
/usr/share/gnome-shell/extensions/disable_account_settings@clip.quarksecurity.com

%post
/usr/bin/gsettings set org.gnome.shell disable-user-extensions true
/usr/bin/dconf update

%postun
dconf update

%changelog
* Tue Mar 26 2019 Kyle Rosales <krosales@localhost.localdomain>
- Initial gnome extensions for CLIP and spec.
