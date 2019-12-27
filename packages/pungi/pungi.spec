%{?python_enable_dependency_generator}

Name:           pungi
Version:        4.1.38
Release:        1%{?dist}.2
Summary:        Distribution compose tool

License:        GPLv2
URL:            https://pagure.io/pungi
Source0:        https://pagure.io/releases/%{name}/%{name}-%{version}.tar.bz2

BuildRequires:  python3-nose
BuildRequires:  python3-mock
%if 0%{?fedora} < 31
BuildRequires:  python2-devel
%endif
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-productmd >= 1.11
BuildRequires:  python3-kobo-rpmlib
BuildRequires:  createrepo_c
BuildRequires:  python3-lxml
BuildRequires:  python3-kickstart
BuildRequires:  python3-rpm
BuildRequires:  python3-dnf
BuildRequires:  python3-multilib
BuildRequires:  python3-six
BuildRequires:  git-core
BuildRequires:  python3-jsonschema
BuildRequires:  python3-libcomps
BuildRequires:  python3-kobo
BuildRequires:  python3-koji
BuildRequires:  python3-unittest2
BuildRequires:  lorax
BuildRequires:  python3-PyYAML
BuildRequires:  libmodulemd < 2
BuildRequires:  python3-gobject-base
BuildRequires:  python3-gobject
BuildRequires:  python3-createrepo_c
BuildRequires:  python3-dogpile-cache
BuildRequires:  python3-parameterized

#deps for doc building
BuildRequires:  python3-sphinx, texlive-collection-fontsrecommended
BuildRequires:  texlive-cmap, texlive-babel-english, texlive-fancyhdr
BuildRequires:  texlive-titlesec, texlive-framed, texlive-threeparttable
BuildRequires:  texlive-mdwtools, texlive-wrapfig, texlive-parskip, texlive-upquote
BuildRequires:  texlive-multirow, texlive-capt-of, texlive-eqparbox
BuildRequires:  tex(fncychap.sty)
BuildRequires:  tex(tabulary.sty)
BuildRequires:  tex(needspace.sty)
BuildRequires:  latexmk

Requires:       python3-kobo-rpmlib
Requires:       python3-kickstart
Requires:       createrepo_c
Requires:       koji >= 1.10.1-13
Requires:       python3-koji-cli-plugins
Requires:       isomd5sum
Requires:       genisoimage
Requires:       git
Requires:       libguestfs-tools-c
Requires:       python3-dnf
Requires:       python3-multilib
Requires:       python3-libcomps
Requires:       python3-koji
Requires:       libmodulemd < 2
Requires:       python3-gobject-base
Requires:       python3-gobject
Requires:       python3-createrepo_c
Requires:       python3-PyYAML

Requires:       python3-%{name} = %{version}-%{release}

BuildArch:      noarch

%description
A tool to create anaconda based installation trees/isos of a set of rpms.

%package utils
Summary:    Utilities for working with finished composes
Requires:   pungi = %{version}-%{release}
Requires:   python3-fedmsg

%description utils
These utilities work with finished composes produced by Pungi. They can be used
for creating unified ISO images, validating config file or sending progress
notification to Fedora Message Bus.


%if 0%{?fedora} < 31
%package legacy
Summary:    Legacy pungi executable
Requires:   %{name} = %{version}-%{release}
Requires:   python2-%{name} = %{version}-%{release}
Requires:   createrepo
Requires:   isomd5sum
Requires:   lorax
Requires:   python2-functools32
Requires:   python2-kickstart
Requires:   python2-kobo
Requires:   python2-libselinux
Requires:   python2-lockfile
Requires:   python2-productmd >= 1.17
Requires:   python2-six
Requires:   repoview
Requires:   xorriso
Requires:   yum
Requires:   yum-utils

%description legacy
Legacy pungi executable. This package depends on Python 2.


%package -n python2-%{name}
Summary:    Python 2 libraries for pungi

%description -n python2-%{name}
Python library with code for Pungi. This is not a public library and there are
no guarantees about API stability.
%endif

%package -n python3-%{name}
Summary:    Python 3 libraries for pungi

%description -n python3-%{name}
Python library with code for Pungi. This is not a public library and there are
no guarantees about API stability.


%prep
%autosetup -p1

%build
%if 0%{?fedora} < 31
%py2_build
%endif
%py3_build
cd doc
make latexpdf SPHINXBUILD=/usr/bin/sphinx-build-3
make epub     SPHINXBUILD=/usr/bin/sphinx-build-3
make text     SPHINXBUILD=/usr/bin/sphinx-build-3
make man      SPHINXBUILD=/usr/bin/sphinx-build-3
gzip _build/man/pungi.1

%install
%if 0%{?fedora} < 31
%py2_install
mv %{buildroot}%{_bindir}/pungi %{buildroot}%{_bindir}/pungi-2
%endif
%py3_install
%if 0%{?fedora} < 31
mv %{buildroot}%{_bindir}/pungi-2 %{buildroot}%{_bindir}/pungi
%endif
%{__install} -d %{buildroot}/var/cache/pungi
%{__install} -d %{buildroot}%{_mandir}/man1
%{__install} -m 0644 doc/_build/man/pungi.1.gz %{buildroot}%{_mandir}/man1

# No utils package for Python 2. On Py 3 this is not installed at all
rm -rf %{buildroot}%{python2_sitelib}/%{name}_utils

    %if 0%{?fedora} > 30
rm %{buildroot}%{_bindir}/pungi
%endif

%check
nosetests-3 --exe

%files
%license COPYING GPL
%doc AUTHORS
%doc doc/_build/latex/Pungi.pdf doc/_build/epub/Pungi.epub doc/_build/text/*
%{_bindir}/%{name}-koji
%{_bindir}/%{name}-gather
%{_bindir}/comps_filter
%{_bindir}/%{name}-make-ostree
%{_mandir}/man1/pungi.1.gz
%{_datadir}/pungi
/var/cache/pungi

%if 0%{?fedora} < 31
%files legacy
%{_bindir}/%{name}

%files -n python2-%{name}
%{python2_sitelib}/%{name}
%{python2_sitelib}/%{name}-%{version}-py?.?.egg-info
%endif

%files -n python3-%{name}
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}-py?.?.egg-info

%files utils
%{python3_sitelib}/%{name}_utils
%{_bindir}/%{name}-create-unified-isos
%{_bindir}/%{name}-config-dump
%{_bindir}/%{name}-config-validate
%{_bindir}/%{name}-fedmsg-notification
%{_bindir}/%{name}-notification-report-progress
%{_bindir}/%{name}-orchestrate
%{_bindir}/%{name}-patch-iso
%{_bindir}/%{name}-compare-depsolving
%{_bindir}/%{name}-wait-for-signed-ostree-handler

%changelog
* Thu Jul 25 2019 Stephen Smoogen <smooge@fedoraproject.org> - 4.1.38-1.2
- Find that I needed to change a libmodulemd elsewhere after it built

* Thu Jul 25 2019 Stephen Smoogen <smooge@fedoraproject.org> - 4.1.38-1.1
- Caveman hack config to make this compile enough for bodhi. Turn libmodulemd to lowest version and tell productmd to be old version.

* Tue Jul 02 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.38-1
- Remove remaining mentions of runroot option (lsedlar)
- pkgset: Include module metadata in the repos (lsedlar)
- config: Deprecate runroot option (hlin)
- Respect --nomacboot flag when calling isohybrid (dnevil)
- config: Keep known options defined on CLI (lsedlar)
- config-dump: Report better error for non-existing sources (lsedlar)
- config: Improve config validation for anyOf and oneOf (lsedlar)
- config-validate: Allow defining variables (lsedlar)
- config: Report validation warning if variants fail to load (lsedlar)
- Allow customizing nosetests command (lsedlar)
- scm: Close stdin of processing command (lsedlar)
- pkgset: Create arch repos in parallel (lsedlar)
- util: Resolve HEAD in repos that have a remote (lsedlar)
- tests: Avoid using threads in tests (lsedlar)
- pkgset: Use highest pickle protocol (lsedlar)
- gather: fix crash issue when gather_method = "nodeps" (hlin)
- pkgset: Check for unused module patterns across all tags (lsedlar)
- util: Fix offline resolving for scm dict (lsedlar)
- pkgset: Make serialization more resilient (lsedlar)
- fus: Support HTTP repos (lsedlar)
- config: Deprecate release_is_layered option (hlin)
- pkgset: Set correct nsvc for devel modules (lsedlar)
- Remove unused variable (lsedlar)
- Whitespace fixes (lsedlar)
- Whitespace cleanup (lsedlar)
- Remove unused variables (lsedlar)
- Remove unused imports (lsedlar)

* Mon May 27 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.37-1
- config-dump: Allow dumping config for multi compose (lsedlar)
- runroot: Remove useless argument output_path (lsedlar)
- buildinstall: Change owner of lorax logs (lsedlar)
- kojiwrapper: Allow changing mode of multiple files (lsedlar)
- buildinstall: Create toplevel directory on compose host (lsedlar)
- arch_utils: add Hygon Dhyana CPU support (fanjinke)
- metadata: Include empty directories in metadata (lsedlar)
- gather: Relax validations on variant_as_lookaside (lsedlar)
- tests: Use correct Python interpreter (lsedlar)
- tests: Ignore warnings when running validation script (lsedlar)
- Remove invalid escape sequences (lsedlar)
- Fix issues in OpenSSH Runroot method found by real tests. (jkaluza)
- buildinstall: Copy files in thread (lsedlar)
- init: Create comps repos in parallel (lsedlar)
- pkgset: Fix whitelist for modules (lsedlar)
- pkgset: Fix filtering excluded modular packages (lsedlar)
- pkgset: Do not overwrite version in module (lsedlar)
- pkgset: Treat modular version as number for sorting (lsedlar)
- Use absolute path for hardlink (lsedlar)
- createiso: Run hardlink on staged content (jdisnard)
- comps-wrapper: Emit attributes sorted (lsedlar)
- patch-iso supports multiple graft directories (jkonecny)

* Thu May 23 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.36-5
- Ignore modules without modulemd in Koji

* Mon May 13 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.36-4
- Include more backported patches

* Tue May 07 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.36-3
- Backport patch for decoding output as UTF-8

* Tue May 07 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.36-2
- Backport fixes for cloning git repos

* Wed Apr 24 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.36-1
- Extend "openssh" runroot_method to be able to execute "mock" (jkaluza)
- osbs: Rework configuration for image pushes (lsedlar)
- Add "openssh" runroot method (jkaluza)
- Fix printing version on Python 3 (lsedlar)
- config-dump: Fix crash when used without --define (lsedlar)
- setup: Fix missing comma in a list (lsedlar)
- setup: Install some deps on Py2.7 only (lsedlar)
- config-dump: Allow defining variables on CLI (lsedlar)
- Update test data (lsedlar)
- gather: Use wildcard for repo selection (lsedlar)
- gather: Apply repo path substitutions for DNF backend (lsedlar)
- tests: Stop overwriting modulesdir for DNF (lsedlar)

* Tue Mar 26 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.35-1
- orchestrator: Monitor status of parts (lsedlar)
- tests: Skip tests if libmodulemd is not available (lsedlar)
- pkgset: Refactor hiding unused modular packages (lsedlar)
- Remove configuration for devel modules (lsedlar)
- gather: Remove module source (lsedlar)
- createrepo: Stop processing modulemd (lsedlar)
- pkgset: Load final modulemd files from Koji (lsedlar)
- buildinstall: Allow overwriting version for lorax (lsedlar)
- Create new Runroot class and use it everywhere where runroot task is
  executed. (jkaluza)
- orchestrator: Send messages about the main compose (lsedlar)
- orchestrator: Support generic pre- and post- scripts (lsedlar)
- orchestrator: Support getting kerberos ticket (lsedlar)
- hybrid: Refactor handling debuginfo packages (lsedlar)
- doc: explain koji_profile (kdreyer)
- pkgset: Stop loading list of module RPMs (lsedlar)
- pkgset: Only load cache once (lsedlar)
- Do not add pkgset_koji_builds to modules, but only to pkgset_koji_tag tags.
  (jkaluza)
- scm: Don't retry git fetch (lsedlar)
- tests: fix metadata tests when SOURCE_DATE_EPOCH is set (marmarek)
- checks: Use GitResolver for scm dicts (lsedlar)
- hybrid: Fix opening gzipped files on Python 2.6 (lsedlar)

* Tue Mar 05 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.34-1
- config: Allow validating configuration in JSON (lsedlar)
- image-build: Accept formats in lists (lsedlar)
- image-build: Resolve git ref in ksurl (lsedlar)
- Resolve git branches in scm_dict (lsedlar)
- util: Refactor resolving git url (lsedlar)
- scm-wrapper: Refactor getting files from Git (lsedlar)
- osbs: Fix wrong message in logs (lsedlar)
- orchestrator: Log exception to log file (lsedlar)
- config-dump: Allow freezing koji event (lsedlar)
- Read koji event from config file (lsedlar)
- osbs: Accept local paths as repo URLs (lsedlar)
- image-build: Support repo/install_tree as path (lsedlar)
- osbs: Remove format requirement for registry (lsedlar)
- orchestrator: Use prefix for config substitutions (lsedlar)
- README: add link to documentation (kdreyer)

* Fri Mar 01 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.33-6
- Update builddep on libmodulemd as well

* Fri Mar 01 2019 Stephen Gallagher <sgallagh@redhat.com> - 4.1.33-5
- Fix libmodulemd dependency

* Wed Feb 27 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.33-4
- Disable legacy and python 2 packages on Fedora 31+

* Mon Feb 25 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.33-3
- Fix copying vmdk images from koji tasks

* Thu Feb 21 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.33-2
- Make it possible to disable Apple/HFS compatibility on ppc64le

* Wed Feb 13 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.33-1
- isos: Check maximum expected size (lsedlar)
- osbs: Process data about pushing images to registries (lsedlar)
- hybrid: Apply filters to debuginfo and source packages (lsedlar)
- hybrid: Get platform from lookaside repos (lsedlar)
- Return RPMs added to -devel module in GatherSourceModule. (jkaluza)
- Allow setting wildcard as a module name in variants to include all the
  modules. (jkaluza)
- gather: Link files in order for dependant variants (lsedlar)
- buildinstall: Pick correct config with rootfs_size (lsedlar)
- hybrid: Add packages from prepopulate to input (lsedlar)
- ostree_installer: Pass --buildarch to lorax (lsedlar)
- orchestrator: Add missing function arguments (lsedlar)
- orchestrator: Compatibility with Python 2.6 (lsedlar)
- pungi-legacy: expose lorax's --rootfs-size argument (frederic.pierret)
- Only require enum34 on Legacy Python (miro)
- ostree: Add test for expanding basearch for message (lsedlar)
- Make sure ${basearch} is also replaced with config['ostree_ref'] (patrick)

* Fri Feb 01 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.32-6
- buildinstall: Pick correct config with rootfs size

* Mon Jan 28 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.32-5
- Pass buildarch to lorax for ostree installer

* Mon Jan 14 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.32-4
- Use python deps generator correctly

* Thu Jan 10 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.32-3
- Replace basearch in ostree ref in message

* Wed Jan 09 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.32-2
- Drop dependency on python3-enum34

* Tue Jan 08 2019 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.32-1
- Add script to orchestrate multiple composes (lsedlar)
- buildinstall: Expose lorax's --rootfs-size argument (lsedlar)
- Support for pungi-legacy with productmd format (frederic.pierret)
- Unify update-docs.sh script with rpkg (onosek)
- Remove createrepo references from doc and spec (lsedlar)
- CreaterepoWrapper: add 'basedir' and 'compress-type' args for createrepo_c
  (frederic.pierret)
- gather.py: use createrepo_c for creating repodata instead of obsolete
  createrepo python library (frederic.epitre)
- Fix import of ConfigParser for NoSectionError and NoOptionError
  (frederic.pierret)
- doc: explain product_id_allow_missing results in detail (kdreyer)
- doc: describe product_id's output and purpose (kdreyer)

* Wed Dec 12 2018 Stephen Gallagher <sgallagh@redhat.com> - 4.1.31-3
- Update dependency for libmodulemd

* Wed Dec 05 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.31-2
- Send correct ostree ref to fedmsg

* Mon Nov 26 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.31-1
- Remove patches keeping old ostree phase ordering
- Add script to merge and dump multiple configuration files (lsedlar)
- Move resolving git reference to config validation (lsedlar)
- util: Add a cache for resolved git urls (lsedlar)
- Copy config files into logs/global/config-copy/ directory (mboddu)
- Remove timestamp from config dump (lsedlar)
- extra_iso: Support extra files in directory (lsedlar)
- extra_iso: Include extra_files.json metadata (lsedlar)
- Allow reading configuration from JSON (lsedlar)
- Cleanup parsing treefile (lsedlar)
- Fix convert rpm_ostree config to YAML (mboddu)
- koji_wrapper: Change owner of runroot output (lsedlar)
- util: Preserve symlinks when copying (lsedlar)
- Move from yaml.load to yaml.safe_load (patrick)
- extra_iso: Stop including variant extra files (lsedlar)
- gather: Expand wildcards in package names for nodeps (lsedlar)
- Configure image name per variant (lsedlar)
- init: Keep parent groups in addon comps environments (lsedlar)
- Support more specific config for devel modules (lsedlar)
- Load supported milestones from productmd (lsedlar)
- hybrid: Remove dead code (lsedlar)
- Remove dead code (lsedlar)

* Wed Oct 31 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.30-1
- gather: Expand wildcards in Pungi (lsedlar)
- repoclosure: Extract logs from hybrid solver (lsedlar)
- gather: Track multilib that doesn't exist (lsedlar)
- Get the NSVC from Koji module CG build metadata (jkaluza)
- extra_iso: Include media.repo and .discinfo (lsedlar)
- hybrid: Don't add debuginfo as langpacks (lsedlar)
- fus: Write solvables to file (lsedlar)
- hybrid: Honor filter_packages (lsedlar)
- Include all test fixtures in source tarball (lsedlar)
- extra-iso: Use correct efiboot.img file (lsedlar)
- extra-iso: Fix treeinfo (lsedlar)
- createiso: Move code for tweaking treeinfo into a function (lsedlar)
- extra-iso: Generate jigdo by default (lsedlar)

* Mon Oct 15 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.29-3
- Save memory less agressively

* Wed Oct 10 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.29-2
- Add dependency on xorriso to pungi-legacy
- Bump dependency on python-productmd

* Wed Oct 10 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.29-1
- hybrid: Only include modules that are not in lookaside (lsedlar)
- Try to be more conservative about memory usage (lsedlar)
- hybrid: Remove modules not listed by fus (lsedlar)
- gather: Make devel modules configurable (lsedlar)
- pkgset: Stop prefilling RPM artifacts (lsedlar)
- gather: Create devel module for each normal module (lsedlar)
- pkgset: Save package set for each module (lsedlar)
- fus: List lookaside repos first (lsedlar)
- gather: Work with repos without location_base (lsedlar)
- Remove extra dependencies (lsedlar)
- Set repodata mtime to SOURCE_DATE_EPOCH (marmarek)
- Make sure .treeinfo file is sorted (marmarek)
- Use constant MBR ID for isohybrid (marmarek)
- Use xorriso instead of genisoimage (marmarek)
- Use $SOURCE_DATE_EPOCH (if set) in discinfo file (marmarek)
- unified_isos: Add extra variants to metadata (lsedlar)
- extra_iso: Add list of variants to metadata (lsedlar)
- linker: Simplify creating pool (lsedlar)
- gather: Hide pid of fus process (lsedlar)
- fus: Strip protocol from repo path (lsedlar)
- Add 'pkgset_koji_builds' option to include extra builds in a compose
  (jkaluza)
- ostree: Reduce duplication in tests (lsedlar)
- ostree: Use --touch-if-changed (lsedlar)
- ostree: Fix handler crash without commit ID (lsedlar)
- gather: Filter arches similarly to pkgset (lsedlar)
- Stop shipping and remove RELEASE-NOTES (pbrobinson)

* Thu Sep 06 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.28-1
- gather: Fix multilib query for hybrid solver (lsedlar)
- gather: Expand multilib lists for hybrid method (lsedlar)
- Index arch modulemd by full NSVC (lsedlar)
- pkgset: Apply whitelist to modules in the tag (lsedlar)
- ostree: Wait for updated ref as well as signature (lsedlar)
- extra_iso: Set unified flag in metadata (lsedlar)
- pkgset: Respect koji event when searching for modules (lsedlar)
- Use dogpile.cache to cache the listTaggedRPMS calls if possible (jkaluza)
- gather: Keep original rpms.json in debug mode (lsedlar)
- Reduce duplication in tests (lsedlar)
- docs: Add better description for package globs (lsedlar)
- Create non-bootable ISO for variant without buildinstall (lsedlar)
- Clean up after yum tests (lsedlar)
- gather: Honor module whitelist (lsedlar)
- Clarify error about non-existing module (lsedlar)
- gather: Print full unresolved dependency (lsedlar)
- Fix tests on Python 2.6 (lsedlar)
- Include all test data in tarball (lsedlar)

* Fri Aug 17 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.27-1
- extra-iso: Rename test data file (lsedlar)
- createiso: Use correct python version (lsedlar)
- ostree: Update tests for working with YAML file (lsedlar)
- pungi/ostree: Convert rpm-ostree YAML to JSON (walters)
- createrepo: Allow passing arbitrary arguments (lsedlar)
- gather: Get modular packages from fus (lsedlar)
- util: Remove escaping spaces from volume ID (lsedlar)
- Allow removing non-alnum chars from volid (lsedlar)
- extra-isos: Include treeinfo pointing to all variants (lsedlar)
- createiso: Use unique paths for breaking hardlinks (lsedlar)
- gather: Detect hybrid variant with additional packages (lsedlar)
- Include exact version of pungi in the logs (mboddu)
- gather: Allow empty result for gather (lsedlar)
- gather: Add langpacks in hybrid solver (lsedlar)
- comps: Add get_langpacks function (lsedlar)
- pungi-legacy: Add --joliet-long option (lsedlar)
- gather: Early exit for non-comps sources (lsedlar)
- tests: Use unittest2 when available (lsedlar)
- buildinstall: Make output world readable (lsedlar)
- buildinstall: Copy file without preserving owner (lsedlar)
- Report failed failable deliverables as errors (lsedlar)
- Stop importing PDCClient (lsedlar)
- spec: build require python-multilib (lsedlar)

* Fri Jul 20 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.26-2
- Backport patch for DNF 3 compatibility
- Fix querying Koji about modules with dash in stream

* Mon Jul 16 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.26-1
- gather: Add a hybrid depsolver backend (lsedlar)
- Always use lookasides for repoclosure (lsedlar)
- doc: closing parentheses for require_all_comps_packages (kdreyer)
- osbs: Generate unique repo names (lsedlar)
- Expand version field during image_build using version_generator (sinny)
- createrepo: Stop including modulemd in debug repos (lsedlar)
- Simplify iterating over module defaults (lsedlar)
- pkgset: Apply module filters on pkgset level (lsedlar)
- init: Validate whitespace in comps groups (lsedlar)
- createrepo: Include empty modules (lsedlar)
- createiso: Break hardlinks by copying files (lsedlar)
- pkgset: Query Koji instead of PDC (mcurlej)
- config: Report variants validity issues (lsedlar)
- variants: Reject values with whitespace (lsedlar)
- osbs: Fresh koji session for getting metadata (lsedlar)
- gather: Ignore comps in lookaside repo (lsedlar)
- init: Test that init phase correctly clones defaults (lsedlar)
- init: Add tests for cloning module defaults (lsedlar)
- init: Add validation for module defaults (lsedlar)
- ostree-installer: Skip comps repo if there are no comps (lsedlar)
- Add test for getting licenses from a repo (lsedlar)
- Add content_licenses to module metadata (sgallagh)
- Update virtualenv instructions (lsedlar)
- Allow extracting koji event from another compose (lsedlar)
- Copy modules instead of reparsing them (sgallagh)
- Silence config warnings in quiet mode (lsedlar)
- osbs: Add nvr to metadata (lsedlar)
- Always get old compose with release type suffix (patrick)
- Make ostree_installer check if buildinstall is skipped correctly (puiterwijk)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.25-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 04 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.25-6
- Add dependency on python2-productmd to legacy subpackage

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 4.1.25-5
- Rebuilt for Python 3.7

* Mon Jun 04 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.25-4
- Call chmod recursively

* Thu May 31 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.25-3
- Don't mark all runroots as successful by chmod

* Wed May 30 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.25-2
- Make results of runroot tasks world readable

* Tue May 22 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.25-1
- comps-wrapper: Make tests pass on EL6 (lsedlar)
- pkgset: Add option to ignore noarch in ExclusiveArch (lsedlar)
- Handling multiple modules with the same NSV - PDC (onosek)
- createrepo: Allow disabling SQLite database (lsedlar)
- init: Drop database from comps repo (lsedlar)
- createrepo: Add module arch to metadata (lsedlar)
- arch: Drop mapping ppc64 -> ppc64p7 (lsedlar)
- arch: Make i386 map to i686 instead of athlon (lsedlar)
- Add a phase for creating extra ISOs (lsedlar)
- Stop using .message attribute on exceptions (lsedlar)
- Validation of parameter skip_phases (onosek)
- Capture sigterm and mark the compose as DOOMED (puiterwijk)
- createiso: Remove useless method (lsedlar)
- createiso: Refactor code into smaller functions (lsedlar)
- arch: Remove mocks in tests (lsedlar)
- ostree-installer: Allow overwriting buildinstall (lsedlar)
- ostree-installer: Work with skipped buildinstall (lsedlar)
- createrepo: Use less verbose logs (lsedlar)
- pkgset: Create global repo in parallel to merging pkgsets (lsedlar)
- createiso: Skip if buildinstall fails (lsedlar)
- Update tests for libmodulemd 1.4.0 (lsedlar)

* Wed May 16 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.24-4
- Use python function to copy ostree installer output

* Thu May 10 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.24-3
- Make wait-for-signed-ostree repeat the fedmsg in case the signer crashed
- Stop filtering comps environments all the time

* Fri May 04 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.24-2
- Copy ostree-installer without preserving owner

* Wed May 02 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.24-1
- koji-wrapper: Log failed subtasks (lsedlar)
- Update compose status when config validation fails (lsedlar)
- pkgset: Allow different inheritance for modules (lsedlar)
- ostree: Recognize force_new_commit option in old config (lsedlar)
- modules: Correctly report error for unexpected modules (lsedlar)
- modules: Allow context in variants XML (lsedlar)
- gather: Print profiling information to stderr (lsedlar)
- pkgset: Stop creating database for repodata (jkaluza)
- gather: Use another variant as lookaside (lsedlar)
- buildinstall: Use metadata if skipped (lsedlar)
- Allow reusing pkgset FileCache from old composes. (jkaluza)
- validation: Populate dict of all variants (lsedlar)
- gather: Stop pulling debuginfo and source for lookaside packages (lsedlar)
- Only use comps repo if we really have comps (lsedlar)
- pkgset: Use modules PDC API (lsedlar)
- Access ci_base date via compose (puiterwijk)
- Allow filtering comps for different variants (lsedlar)
- comps: Make filtering by attribute more generic (lsedlar)
- pkgset: Dump downloaded modulemd to logs (lsedlar)
- Fix PEP8 warning about if not x in y (lsedlar)
- Variant as a lookaside - configuration (onosek)
- Remove comps from arch repo (lsedlar)
- init: Stop creating module defaults dir twice (lsedlar)
- gather: Reduce logs from DNF gathering (lsedlar)
- Clone module defaults into work/ directory (lsedlar)
- Update the configuration JSON schema for module_defaults_dir (contyk)
- Update configuration docs with module_defaults_dir (contyk)
- Handle relative paths in module_defaults_dir (contyk)
- Include module defaults in the repodata (contyk)
- Add *.in fixtures to tarball (lsedlar)
- init: Always filter comps file (lsedlar)
- docs: Describe comps processing (lsedlar)
- gather: Use comps for given variant (lsedlar)
- docs: Fix typo (lsedlar)
- Add all packages to whitelist for hybrid variant (lsedlar)
- comps: Add tests for CompsFilter (lsedlar)
- comps: Move filtering into wrapper module (lsedlar)
- Tests fail if unittest2 library is missing (onosek)
- Add unittest2 and rpmdevools to contributing doc (rmarshall)
- pkgset: Construct UID for PDC modules (lsedlar)
- gather: Simplify creating temporary directory (lsedlar)
- buildinstall: Add extra repos (lsedlar)
- tests: Use dummy modulesdir for DNF (lsedlar)
- Update tests for Python 2.6 (onosek)

* Tue Apr 24 2018 Kevin Fenzi <kevin@scrye.com> - 4.1.23-5
- Backport fix for Accessing ci_base date via compose
- https://pagure.io/pungi/pull-request/910

* Thu Apr 12 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.23-4
- Stop creating module defaults dir twice

* Thu Apr 12 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.23-3
- Add support for module defaults

* Wed Apr 11 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.23-2
- Revert reordering of ostree phases

* Wed Apr 4 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.23-1
- Update documentation section 'contributing' (onosek)
- Write module metadata (onosek)
- Support multilib in GatherSourceModule (jkaluza)
- ostree: Always substitute basearch (lsedlar)
- If sigkeys is specified, require at least one (puiterwijk)
- Allow setting <kojitag/> in <modules/> in variants.xml to get the modules
  from this Koji tag. (jkaluza)
- Move Modulemd import to pungi/__init__.py to remove duplicated code.
  (jkaluza)
- Use Modulemd.Module for 'variant.arch_mmds' instead of yaml dump (jkaluza)
- Fix modular content in non-modular variant (lsedlar)
- Remove the filtered RPMs from module metadata even in case all RPMs are
  filtered out. (jkaluza)
- pkgset: Allow empty list of modules (lsedlar)
- buildinstall: Add option to disable it (lsedlar)
- Use libmodulemd instead of modulemd Python module (jkaluza)
- gather: Fix package set whitelist (lsedlar)
- pkgset: Merge initial package set without checks (lsedlar)
- pkgset: Remove check for unique name (lsedlar)
- gather: Honor package whitelist (lsedlar)
- Write package whitelist for each variant (lsedlar)
- image-build: Accept tar.xz extension for docker images (lsedlar)
- pkgset: Correctly detect single tag for variant (lsedlar)
- Remove comps groups from purely modular variants (lsedlar)
- gather: Allow filtering debuginfo packages (lsedlar)
- Move ostree phase and pipelines for running phases (onosek)
- Other repo for OstreeInstaller (onosek)
- Add modulemd metadata to repo even without components (jkaluza)
- Correct fix for volume ID substition sorting by length (awilliam)
- Ordering processing for volume ID substitutions (onosek)
- Disable multilib for modules (jkaluza)
- scm: Stop decoding output of post-clone command (lsedlar)
- Remove useless shebang (lsedlar)
- source_koji.py: Properly handle unset pkgset_koji_tag (otaylor)
- pkgset: Only use package whitelist if enabled (lsedlar)
- Fail early if input packages are unsigned (jkaluza)
- Allow composing from tag with unsigned packages (jkaluza)
- Ostree can use pkgset repos (onosek)
- Support multiple sources in one variant (lsedlar)
- gather: Set lookaside flag focorrectly (lsedlar)
- gather: Try getting srpm from the same repo as rpm (lsedlar)
- Minor correction for python backward compatibility (onosek)

* Fri Mar 23 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-10.1
- Always substitute basearch in ostree

* Fri Mar 16 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-10
- Fix package whitelist for non-modular variants

* Wed Mar 14 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-9
- Allow empty modular variants
- Add option to disable multilib

* Fri Mar 09 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-8
- Fix package set whitelist

* Thu Mar 08 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-7
- image-build: Accept tar.xz extension for docker images
- Allow multiple versions of the same package in package set

* Tue Mar 06 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-6
- Speed up compose with modules

* Fri Mar 02 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-5
- Remove comps groups from purely modular variants

* Wed Feb 21 2018 Dennis Gilmore <dennis@ausil.us> - 4.1.22-4
- make pungi-utils require python3-fedmsg

* Tue Feb 06 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-3
- Add support for mixing traditional and modular content

* Mon Feb 5 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-2
- Create a subpackage with legacy pungi command

* Wed Jan 24 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.22-1
- Better INFO messages about modules (onosek)
- Updates composes should be marked as supported (lsedlar)
- pkgset: Only add missing packages from global tag (lsedlar)
- ostree/utils: Drop timestamps from generated repo names - tests (onosek)
- ostree/utils: Generate a single pungi.repo file, use repo-<num> IDs (walters)
- ostree/utils: Drop timestamps from generated repo names (walters)
- gather: Do not require variant for module source (lsedlar)
- gather: Comps source should not crash without comps file (lsedlar)
- gather: JSON source returns nothing without configuration (lsedlar)
- buildinstall: Fix treeinfo generating on failure (lsedlar)
- Add buildinstall_use_guestmount boolean option (jkaluza)
- gather: Use arch packages in nodeps method (lsedlar)
- pkgset: Always use global tag if specified (lsedlar)
- config: Make pkgset_koji_tag optional (lsedlar)
- ostree: Add force_new_commit option - test added (onosek)
- ostree: Add force_new_commit option (walters)
- gather: Fix checking string type (lsedlar)
- Improve logging for unsigned packages (onosek)
- Fall back to mount if guestmount is not available (onosek)
- El-Torito boot information on s390x (onosek)
- Remove strace from buildinstall runroot (onosek)
- doc: fix "Miscellaneous" spelling in Config section (kdreyer)
- doc: move "Phases" up, "Contributing" down (kdreyer)

* Tue Jan 16 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.21-4
- Add option to force fallback from guestmount

* Wed Jan 10 2018 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.21-3
- Fix checking string type in nodeps method

* Wed Dec 13 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.21-2
- Remove /usr/bin/pungi
- Remove dummy compose from check section

* Wed Dec 06 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.21-1
- tests: Use correct python version for config validation test (lsedlar)
- Use dnf backend for repoclosure on PY3 (lsedlar)
- Drop checks for git and cvs (lsedlar)
- Relax check for gettext (lsedlar)
- Drop check for repoquery command (lsedlar)
- Use modifyrepo_c if possible (lsedlar)
- pkgset: Add SRPMs to whitelist (lsedlar)
- modules: Allow multilib (lsedlar)
- add ability to specify ostree ref in OSTREE phase - update (onosek)
- add ability to specify ostree ref in OSTREE phase (onosek)
- buildinstall: Allow using external dire for runroot task (jkaluza)
- pkgset: Remove package skip optimization for bootable products (lsedlar)
- Add documentation for modular composes (lsedlar)
- osbs: Get correct path to repo for addons (lsedlar)
- Remove deprecated options (onosek)
- module-source: Log details about what packages are gathered (lsedlar)
- gather: Log details about nodeps method (lsedlar)
- gather: get_packages_to_gather returns a tuple (lsedlar)
- iso-wrapper: Fix calling wrong logger method (lsedlar)
- Turn COMPOSE_ID version generator into DATE_RESPIN (puiterwijk)
- iso-wrapper: Remove hacks for sorting (lsedlar)
- Report missing module dependencies earlier (lsedlar)
- Implement version.compose_id version generator (patrick)
- Optionally do old_compose per release type (patrick)

* Wed Nov 22 2017 Patrick Uiterwijk <puiterwijk@redhat.com> - 4.1.20-3
- Backport patch for PR#790 - old_composes per release type
- Backport patch for PR#791,796 - implement DATE_RESPIN version generator

* Tue Nov 21 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.20-2
- Fix crash in modular compose

* Wed Nov 01 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.20-1
- image-build: Drop suffixes from configuration (lsedlar)
- kojiwrapper: Deal with multiple values for image-build (lsedlar)
- Add modulemd to the missing module error (patrick)
- notification: Add more info into the messages (lsedlar)
- notification: Fix running on Python 3 (lsedlar)
- remove remaining hard coded createrepo threads (onosek)
- tests: Fix remaining missing assertions (lsedlar)
- tests: Work with older unittest2 (lsedlar)
- tests: Skip testing pdc logs if dependencies are not installed (lsedlar)
- Log PDC communications and info for modular composes (dowang)
- Update documentation section "Contributing to Pungi". (onosek)
- Reject yum gather backend on Python 3 (lsedlar)
- Stop using deprecated pipes.quote (lsedlar)
- Convert configparser values to string (lsedlar)
- Explicitly decode test files as UTF-8 (lsedlar)
- Use universal_newlines when running other commands (lsedlar)
- Port to Python 3 (lsedlar)
- checks: Use list of release types from productmd (patrick)
- Add an option to make pungi-koji print its compose_dir to stdout (patrick)
- buildinstall: Expose template arguments for lorax (lsedlar)
- Add support for new modules naming policy with colon delimiter (jkaluza)
- Catch the issue when PDC does not contain RPMs, but the module definition
  says there should be some. (jkaluza)
- pkgset: Cherry-pick packages from Koji when we know already what packages
  will end up in compose (jkaluza)
- config: Allow comps_file for any gather_source (lsedlar)
- pkgset: Allow unsigned packages by empty key (lsedlar)
- gather: Nodeps should allow noarch packages (lsedlar)
- pkgset: Clean up path generation (lsedlar)
- createiso: Fix logging for media split (lsedlar)
- Raise the Exception when a symlink cannot be created. (randy)
- Use variant UID for subvariant fallback (lsedlar)
- Fixup for opening config dumps (lsedlar)
- Open and close file descriptors. (rbean)
- live-images: Honor global settings for target (lsedlar)
- unified-isos: Stop erasing metadata on failure (lsedlar)
- Add directory name for checksum file (lsedlar)
- createrepo: Allow customizing number of threads (lsedlar)
- Make ostree installer before cloud images (lsedlar)

* Mon Oct 23 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.19-4
- Expose template arguments for lorax

* Wed Oct 18 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.19-3
- Allow comps_file for any gather_source

* Mon Oct 02 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.19-2
- Update dependencies for EPEL 7

* Wed Sep 20 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.19-1
- docs: Mention how input package list are interpreted (lsedlar)
- Fix pungi-koji --version (dowang)
- profiler: Fix sorting on Python 3 (lsedlar)
- util: Fix timezone offset (lsedlar)
- gather(dnf): Remove dead code (lsedlar)
- gather(dnf): Don't exclude packages from lookaside (lsedlar)
- gather(yum): Don't exclude packages from lookaside (lsedlar)
- gather: Add tests for excluding packages from lookaside (lsedlar)
- gather: Capture broken deps in test (lsedlar)
- gather-dnf: Warn about unresolvable dependencies (lsedlar)
- Fix formatting timezone offset (lsedlar)
- Add timezone info into logs (lsedlar)
- log: save imported config files too (qwan)
- ostree-installer: Only run on empty variants (lsedlar)
- Allow extracting profiling information from pungi-gather. (rbean)
- createrepo: Only consider successful compose for deltas (lsedlar)
- createrepo: Allow selecting variants for delta RPMs (lsedlar)
- createrepo: Only create delta RPMs for binary repos (lsedlar)
- image-build: add arch name(s) in image config file name (qwan)
- Check for correct string class (lsedlar)
- Open files as binary where needed (lsedlar)
- buildinstall: No copy if task fails (lsedlar)
- config: Allow setting default compose type (lsedlar)
- Use Py3-compatible exception handling (lsedlar)
- Use Python 3 print function (lsedlar)
- docs: Abort update script on error (lsedlar)

* Tue Aug 22 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.18-1
- KojiWrapper: include serverca in session_opts (otaylor)
- Report warning when config sections are not used (lsedlar)
- pkgset: Download packages with dnf (lsedlar)
- gather: Fix duplicated log line (lsedlar)
- gather: Add fulltree-exclude flag to DNF backend (lsedlar)
- checks: Stop looking for imports (lsedlar)
- ostree: Simplify configuration (lsedlar)
- config: Reduce duplication in schema (lsedlar)
- config: Add option for dumping config schema (lsedlar)
- scm: Accept unicode as local path (lsedlar)
- docs: Add documentation for scm_dict (lsedlar)
- scm-wrapper: Allow running command after git clone (lsedlar)
- scm-wrapper: Test correct file lists are returned (lsedlar)
- tests: Fix test_compose.sh paths (lsedlar)
- gather: Only parse pungi log once (lsedlar)
- gather: Report missing comps packages (lsedlar)
- gather: Avoid reading whole log into memory (lsedlar)
- repoclosure: Allow aborting compose when repoclosure fails (lsedlar)
- repoclosure: Fix logging errors (lsedlar)
- tests: Make test-compose cwd independent (lsedlar)
- Make strict the only option. (rbean)
- Raise a ValueError with details if module not found in PDC. (rbean)
- unified-iso: Only link to non-empty variants (lsedlar)
- gather: Fix excluding debugsource packages from input list (lsedlar)
- gather: Add debugsource package to tests (lsedlar)
- Use only one list of patterns/rules for debug packages (opensource)
- Do not match "*-debugsource-*" as debuginfo package (opensource)
- Use pungi.util.pkg_is_debug() instead of pungi.gather.is_debug() (opensource)
- remove the dependency of rpmUtils (qwan)
- Add support for debugsource packages (lsedlar)
- gather: Don't pull multiple debuginfo packages (lsedlar)
- GatherSourceModule: return rpm_obj instead of the rpm_obj.name (jkaluza)
- gather: Stop requiring comps file in nodeps (lsedlar)

* Wed Aug 09 2017 Dusty Mabe <dusty@dustymabe.com> - 4.1.17-4
- Add requires on python3-koji-cli-plugins for koji runroot plugin

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.17-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 20 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.17-2
- Fixes for modular compose with gather nodeps method

* Mon Jul 17 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.17-1
- checksum: Checksum each image only once (lsedlar)
- checksum: Refactor creating checksum files (lsedlar)
- createrepo: Don't use existing metadata with deltas (lsedlar)
- util: Fix finding older compose (lsedlar)
- createrepo: Use correct paths for old package dirs (lsedlar)
- spec: Add missing ostree signature waiting handler (lsedlar)
- docs: Minor improvements to documentation (lsedlar)
- ostree: Add notification handler to wait for signature (lsedlar)
- ostree: Add URL to repo to message (lsedlar)
- gather: nodeps should take packages from comps groups (lsedlar)
- unified-iso: handle empty arch (kdreyer)
- createrepo: handle missing product ids scm dir (kdreyer)
- comps_wrapper: Code clean up (lsedlar)
- comps_filter: Filter environments by arch (pholica)
- notification: Allow specifying multiple scripts (lsedlar)
- pkgset: Allow populating packages from multiple koji tags (qwan)
- pungi: Port to argparse (lsedlar)
- comps_filter: Port to argparse (lsedlar)
- variants-wrapper: Remove main() function (lsedlar)
- multilib_yum: Remove main() function (lsedlar)
- pungi-koji: Port to argparse (lsedlar)
- ostree: Update tests for no ostree init (lsedlar)
- ostree: Don't automatically create a repo (walters)
- osbs: Config validation should accept a list (lsedlar)
- pkgset: Use release number of a module (mcurlej)
- docs: Add a basic info about gathering packages (lsedlar)
- docs: Kobo can be installed via pip now (lsedlar)
- docs: Add overview of what each phase does (lsedlar)
- gather: Log tag from which we pulled a package (lsedlar)
- docs: Document config file format (lsedlar)
- docs: Move logo to _static subdir (lsedlar)
- gather: Display source repo of packages (lsedlar)
- pkgset: Use descriptive name for log file (lsedlar)
- ostree-installer: Clean up output dir (lsedlar)
- Ignore more pycodestyle warnings (lsedlar)
- Allow gather source classes to return SimpleRpmWrapper objects from pkgset
  phase directly. (jkaluza)
- tests: use unittest2 if available (lsedlar)

* Mon Jun 19 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.16-3
- Add dropped livemedia phase

* Tue Jun 13 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.16-2
- Handle failed subtasks when getting Koji results

* Mon Jun 12 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.16-1
- Fix changelog generator script (lsedlar)
- util: Retry resolving git branches (lsedlar)
- arch: Move exclu(de|sive)arch check to a function (lsedlar)
- gather-source: Check arch in module source (jkaluza)
- koji-wrapper: Stop mangling env variables (lsedlar)
- Ensure all phases are stopped (lsedlar)
- comps-wrapper: Report unknown package types (lsedlar)
- Generate proper modular metadata when there are different versions of the
  same package in the variant (jkaluza)
- checks: Make gpgkey a boolean option (lsedlar)
- ostree: Refactor writing repo file (lsedlar)
- iso-wrapper: Capture debug information for mounting (lsedlar)
- comps-wrapper: Fix crash on conditional packages (lsedlar)
- gather: Don't resolve dependencies in lookaside (lsedlar)
- koji-wrapper: Run all blocking commands with fresh ccache (lsedlar)
- Add @retry decorator and use it to retry connection on PDC on IOError and in
  SCM's retry_run. (jkaluza)
- Remove shebang from non-executable files (lsedlar)

* Mon Jun 05 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.15-2
- Ensure proper exit on failure

* Fri May 05 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.15-1
- pkgset: Remove use of undefined variable (lsedlar)
- Store RPM artifacts in resulting repository in modulemd metadata. (jkaluza)
- variants: Remove redundant check (lsedlar)
- compose: Stop duplicating variant types (lsedlar)
- gather: Remove handling of impossible state (lsedlar)
- gather: Clean up code (lsedlar)
- gather: Add tests for gather phase (lsedlar)
- scm-wrapper: Remove unused arguments (lsedlar)
- tests: Avoid creating unused temporary files (lsedlar)
- tests: Clean up persistent temporary data (lsedlar)
- docs: Add a logo on the About page (lsedlar)
- docs: Document origin of the name (lsedlar)
- gather-dnf: Log exact Requires pulling a package in (lsedlar)
- gather: Print specific Requires which pulls a package in (lsedlar)
- gather: Process dependencies sorted (lsedlar)
- koji-wrapper: Run koji runroot with fresh credentials cache (lsedlar)
- util: Move get_buildroot_rpms to koji wrapper (lsedlar)
- osbs: Make git_branch required option (lsedlar)
- docs: Update createrepo_checksum allowed values (lsedlar)
- extra-files: Allow configuring used checksums (lsedlar)
- doc: Document options for media checksums (lsedlar)
- config: Add sha512 as valid createrepo checksum (lsedlar)
- util: Report better error on resolving non-existing branch (lsedlar)
- util: Show choices for volid if all are too long (lsedlar)
- checks: Fix anyOf validator yield ValidationError on ConfigOptionWarning
  (qwan)
- comps-wrapper: Reduce duplication in code (lsedlar)
- comps-wrapper: Port to libcomps (lsedlar)
- comps-wrapper: Sort langpacks by name (lsedlar)
- comps-wrapper: Minor code cleanup (lsedlar)
- comps-wrapper: Add tests (lsedlar)
- comps-wrapper: Fix uservisible not being modifiable (lsedlar)
- comps-wrapper: Return IDs instead of yum.comps.Group (lsedlar)
- comps-wrapper: Remove unused code (lsedlar)
- Be explicit about generating release for images (lsedlar)
- docs: Add examples for generated versions (lsedlar)
- ostree: Autogenerate a version (lsedlar)
- Expand compatible arches when gathering from modules. (rbean)
- gather: Clean up method deps (lsedlar)
- gather: Report error if there is no input (lsedlar)
- init: Warn when variants mentions non-existing comps group (lsedlar)
- Fix createrepo issue for modular compose when multiple threads tried to use
  the same tmp directory. (jkaluza)
- unified-iso: Use different type for debuginfo iso (lsedlar)
- unified-iso: Handle missing paths in metadata (lsedlar)
- unify repo and repo_from options (qwan)
- Fix some PEP8 errors in util.py (qwan)
- move translate_path from paths.py to util.py (qwan)
- checks.py: support 'append' option (qwan)
- checks.py: show warning message for alias option (qwan)

* Thu Apr 13 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.14-3
- Expand compatible arches when gathering from modules

* Tue Apr 11 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.14-2
- Fix createrepo issue for modular compose

* Tue Mar 28 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.14-1
- Not create empty skeleton dirs for empty variants (qwan)
- Query only active modules in PDC. (jkaluza)
- Save modules metadata as full yaml object (jkaluza)
- Implement DNF based depsolving (dmach, mmraka, lsedlar)
- Add support for modular composes (jkaluza)
- Add a script for modifying ISO images (lsedlar)
- iso-wrapper: Add utility for mounting images (lsedlar)
- buildinstall: Move tweaking configs into a function (lsedlar)
- image-build: Correctly write can_fail option (lsedlar)
- pungi-koji: new cmd option '--latest-link-status' (qwan)
- Print task ID for successful tasks (lsedlar)
- ostree-installer: Fix logging directory (lsedlar)
- buildinstall: Print debug info if unmount fails (lsedlar)
- pkgset: report all unsigned packages (qwan)
- default createrepo_checksum to sha256 (qwan)
- unified-iso: Log better error when linking fails (lsedlar)
- unified-iso: Blacklist extra files metadata (lsedlar)
- buildinstall: Retry unmounting image (lsedlar)
- Remove indices from documentation (lsedlar)
- iso-wrapper: Handle wrong implant md5 (lsedlar)
- image-build: Remove check for number of images (lsedlar)
- Extract only first version from specfile (lsedlar)
- consolidate repo option names (qwan)
- checks: extend validator with 'alias' (qwan)
- osbs: write manifest for scratch osbs (qwan)

* Mon Mar 06 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.13-2
- Remove check for number of images

* Mon Mar 06 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.13-1
- Make MANIFEST.in stricter (qwan)
- Remove one line of log print (qwan)
- gather: Filter comps group on depsolving input of optional (lsedlar)
- Enable customizing runroot task weight (lsedlar)
- comps: Filter comps groups for optional variants (lsedlar)
- Rename main logger (lsedlar)
- ostree: Silence logger in tests (lsedlar)
- ostree: Fix crash when extra repos are missing (lsedlar)
- util: Add a utility for managing temporary files (lsedlar)
- Add --quiet option to pungi-koji (qwan)
- handle opening empty images.json while re-running pungi-koji in debug mode
  (qwan)
- minor change: remove an always true condition (qwan)
- Refactor depsolving tests (lsedlar)
- multilib: Remove FileMultilibMethod class (lsedlar)
- pkgset: Use additional packages for initial pull (lsedlar)
- metadata: Fix .treeinfo paths for addons (lsedlar)
- koji_wrapper: Always use --profile option with koji (lsedlar)
- add missing koji_profile from test compose setting (dennis)
- use koji --profile when calling koji for livemedia (dennis)
- repoclosure: Don't run build deps check (lsedlar)
- repoclosure: add option to use dnf backend (lsedlar)
- repoclosure: Add test for repoclosure in test phase (lsedlar)
- repoclosure: Remove duplicated code (lsedlar)
- repoclosure: Remove useless wrapper class (lsedlar)
- repoclosure: Remove unused code (lsedlar)
- repoclosure: Add a test for the wrapper (lsedlar)
- image-build: Pass arches around as a list (lsedlar)
- image-build: Expand arches for can_fail (lsedlar)
- image_checksum: add file sizes to checksum files (qwan)
- Add documentation and example for greedy_method (lsedlar)
- replace ${basearch} when updating the ref (dennis)
- Add some debugging about ref updating (puiterwijk)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 24 2017 Dennis Gilmore <dennis@ausil.us> - 4.1.12-4
- add patches for pagure pr#517

* Tue Jan 17 2017 Dennis Gilmore <dennis@ausil.us> - 4.1.12-3
- add patch to replace ${basearch} in the ostree ref

* Tue Jan 17 2017 Dennis Gilmore <dennis@ausil.us> - 4.1.12-2
- add patch from Patrick to give us some ostree debuging

* Tue Jan 17 2017 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.12-1
- unified-iso: Fall back to default config (lsedlar)
- osbs: optionally check GPG signatures (qwan)
- ostree-installer:  Allow multiple repos in ostree installer (qwan)
- Update tox.ini (lsedlar)
- unified-iso: Create isos with debuginfo packages (lsedlar)
- Create temporary dirs under compose's workdir (qwan)
- spec: Update upstream and source URL (lsedlar)
- unified-iso: Create work/ dir if missing (lsedlar)
- spec: Copy %%check section from Fedora (lsedlar)
- Update MANIFEST.in to include test data (lsedlar)
- osbs: Add better example to documentation (lsedlar)
- metadata: Correctly parse lorax .treeinfo (lsedlar)
- spec: Add a separate subpackage for extra utils (lsedlar)
- Add script to generate unified ISOs (lsedlar)
- osbs: Validate config in tests (lsedlar)
- osbs: Verify the .repo files contain correct URL (lsedlar)
- osbs: Enable specifying extra repos (lsedlar)
- pungi-make-ostree: change 'tree' command '--log-dir' arg to be required
  (qwan)
- Add test for krb_login with principal and keytab (puiterwijk)
- Make sure that the profile name is parsed correctly (puiterwijk)
- Make KojiWrapper support krb_login with keytab (puiterwijk)
- Make KojiWrapper parse krb_rdns (puiterwijk)
- Update documentation (lsedlar)
- image-build: Allow failure only on some arches (lsedlar)
- live-media: Allow some arches to fail (lsedlar)
- image-build: Use install_tree from parent for nested variants (lsedlar)
- config: Report unknown options as warnings (lsedlar)
- pungi: Fix --nosource option (lsedlar)
- pungi: Handle missing SRPM (lsedlar)
- ostree-installer: Add 'installer' sub-command to pungi-make-ostree (qwan)
- ostree: Add 'tree' sub-command to pungi-make-ostree script (qwan)
- metadata: Allow creating internal releases (lsedlar)
- Add CLI option to create ci compose (lsedlar)
- Fix PhaseLoggerMixin in case of compose has _logger = None (qwan)
- ostree-installer: Use dvd-ostree as type in metadata (lsedlar)
- image-build: Reduce duplication (lsedlar)
- createrepo: Add tests for adding product certificates (lsedlar)
- createrepo: Add tests for retrieving product certificates (lsedlar)
- Include phase name in log for some phases (qwan)
- Expose lorax's --rootfs-size argument (walters)
- pungi: Include noarch debuginfo (lsedlar)
- media-split: Print sensible message for unlimited size (lsedlar)

* Wed Dec 14 2016 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.11-4
- Add patches for koji kerberos auth

* Thu Dec 08 2016 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.11-3
- Backport patches for ostree installer

* Mon Nov 21 2016 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.11-2
- Add missing dependency on libguestfs-tools-c

* Tue Nov 15 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.11-1
- [ostree] Allow extra repos to get packages for composing OSTree repository
  (qwan)
- pungi: Run in-process for testing (lsedlar)
- pungi: Only add logger once (lsedlar)
- pungi: Connect yum callback to logger (lsedlar)
- extra-files: Nice error message on missing RPM (lsedlar)
- compose: Drop unused argument (lsedlar)
- compose: Search all nested variants (lsedlar)
- ostree-installer: Capture all lorax logs (lsedlar)
- lorax-wrapper: Put all log files into compose logs (lsedlar)
- pungi: Fix reading multilib config files (lsedlar)
- pungi: Fulltree should not apply for input multilib package (lsedlar)
- pungi: Add tests for depsolving (lsedlar)
- Update ostree phase documentation (lsedlar)
- [ostree] Allow adding versioning metadata (qwan)
  (lubomir.sedlar)
- [ostree] New option to enable generating ostree summary file (qwan)
- pungi: Avoid removing from list (lsedlar)
- pungi: Allow globs in %%multilib-whitelist (dmach)
- pungi: Exclude RPMs that are in lookaside (dmach)
- pungi: Fix excluding SRPMs (dmach)
- pungi: Speed up blacklist processing (dmach)
- Update tests to use ostree write-commit-id (puiterwijk)
- ostree: Use the write-commitid-to feature rather than parsing ostree logs
  (puiterwijk)
- checks: Check for createrepo_c (lsedlar)
- checks: Update tests to not require python modules (lsedlar)
- Remove executable permissions on test scripts (puiterwijk)
- Add more require checks (puiterwijk)
- Fix package name for createrepo and mergerepo (puiterwijk)
- not using 'git -C path' which is not supported by git 1.x (qwan)
- pungi-koji: add option for not creating latest symbol link (qwan)
- Replace mount/umount with guestfsmount and 'fusermount -u' (qwan)
- config: Don't abort on deprecated options (lsedlar)
- metadata: Treeinfo should point to packages and repo (lsedlar)
- Send notification when compose fails to start (lsedlar)
- metadata: Stop crashing for non-bootable products (lsedlar)
- createiso: Do not split bootable media (lsedlar)
- doc: Fix a typo in progress notification example (lsedlar)
- Dump images.json after checksumming (lsedlar)
- metadata: Correctly clone buildinstall .treeinfo (lsedlar)
- createiso: Include layered product name in iso name (lsedlar)
- buildinstall: Only transform arch for lorax (lsedlar)
- iso-wrapper: Remove the class (lsedlar)
- config: Validate variant regular expressions (lsedlar)

* Sat Oct 08 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.10-1
- pungi: Replace kickstart repo url (mark)
- ostree-installer: Reduce duplication in tests (lsedlar)
- ostree-installer: Generate correct volume ID (lsedlar)
- ostree-installer: Use ostree as type in filename (lsedlar)
- ostree: Use $basearch in repo file (lsedlar)
- config: Accept empty branch in SCM dict (lsedlar)
- Remove duplicated version from pungi script (lsedlar)
- use --new-chroot when making ostree's (dennis)
- Create git tags without release (lsedlar)
- Translate paths without double slash (lsedlar)
- Remove shebangs from non-executable files (lsedlar)
- Remove FSF address from comments (lsedlar)
- Update contributing guide (lsedlar)
- init: Remove keep_original_comps option (lsedlar)
- tests: Use unittest2 consistently (lsedlar)

* Thu Sep 29 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.9-2
- add patch to enable use of --new-chroot for ostree tasks

* Wed Sep 21 2016 Lubomír Sedlář <lsedlar@redhat.com> - 4.1.9-1
- ostree_installer: Add --isfinal lorax argument (lsedlar)
- Recreate JSON dump of configuration (lsedlar)
- Merge #385 `Test and clean up pungi.linker` (dennis)
- Merge #390 `checksums: Never skip checksumming phase` (dennis)
- variants: Allow multiple explicit optional variants (lsedlar)
- checksums: Never skip checksumming phase (lsedlar)
- [linker] Remove dead code (lsedlar)
- [linker] Add tests (lsedlar)
- Dump original pungi conf (cqi)
- ostree: Add tests for sending ostree messages (lsedlar)
- Send fedmsg message on ostree compose finishg (puiterwijk)
- createrepo: Add option to use xz compression (lsedlar)
- Allow user to set a ~/.pungirc for some defaults (riehecky)
- metadata: Improve error reporting on failed checksum (lsedlar)
- extra-files: Write a metadata file enumerating extra files (jeremy)
- Merge #381 `Automatically generate missing image version` (dennis)
- Automatically generate missing image version (lsedlar)
- Add JSON Schema for configuration (lsedlar)
- Allow arbitrary arguments in make test (lsedlar)
- createiso: Report nice error when tag does not exist (lsedlar)
- Fix test data build script (lsedlar)
- [osbs] Add NVRA of created image into main log (lsedlar)
- [createiso] Remove unused script (lsedlar)
- Update doc about generating release value (lsedlar)
- Use label to populate image release (lsedlar)
- doc: Fix example for image_build (lsedlar)
- Ignore module imports not at top of file (lsedlar)
- Merge #367 `Remove unused imports` (dennis)
- [buildinstall] Fix cleaning output dir (lsedlar)
- Remove unused imports (lsedlar)
- Merge #360 `[osbs] Convert build_id to int` (dennis)
- Merge #361 `Fix config validation script` (dennis)
- Merge #365 `Make image test at end of compose less strict` (dennis)
- [test] Make image test at end of compose less strict (lsedlar)
- [iso] Fix check on failable ISO (lsedlar)
- Add full Pungi version to log output (lsedlar)
- Fix config validation script (lsedlar)
- [osbs] Convert build_id to int (lsedlar)
- [image-build] Get failable config from correct place (lsedlar)

* Wed Aug 10 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.8-1
- [createiso] Use shell script for runroot (lsedlar)
- Merge #357 `Improve error messages for gathering packages` (dennis)
- [test] Only check bootability for images on x86_64 and i386 (lsedlar)
- Improve error messages for gathering packages (lsedlar)
- Merge #339 `Refactor failables, step 1` (dennis)
- Refactor failables (lsedlar)
- Stop setting release in OSBS phase (lsedlar)
- Merge #351 `Remove ambiguous imports` (dennis)
- [test] Correctly check bootable ISOs (lsedlar)
- Remove ambiguous imports (lsedlar)
- Merge #347 `Remove duplicate definition of find_old_composes.`
  (lubomir.sedlar)
- Merge #342 `Simplify naming format placeholders` (dennis)
- Merge #345 `createrepo: use separate logs for different pkg_type` (dennis)
- Remove duplicate definition of find_old_composes... (rbean)
- [createrepo] fix 'createrepo_deltas' option (qwan)
- createrepo: use separate logs for different pkg_type (lsedlar)
- Simplify naming format placeholders (lsedlar)
- Treat variants without comps groups as having all of them (lsedlar)
- Always generate rpms.json file (lsedlar)

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.1.7-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Jun 23 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.7-1
- [scm] Add logging for exporting local files (lsedlar)
- [extra-files] Only copy files when there is a config (lsedlar)
- [extra-files] Refactoring (lsedlar)
- [extra-files] Skip whole phase if not configured (lsedlar)
- [extra-files] Copy files using existing function (lsedlar)
- [extra-files] Add tests (lsedlar)
- [osbs] Add a phase to build images in OSBS (lsedlar)
- Setup global log file before logging anything (lsedlar)
- [metadata] Correctly save final flag (lsedlar)
- Merge #326 `add missing dependencies` (dennis)
- [createiso] Add test for adding source iso to metadata (lsedlar)
- Merge #325 `Fix checking optional ISO images in test phase` (dennis)
- Merge #321 `Add support for top-level variant IDs with dashes.` (dennis)
- Merge #320 `images.json: Move src images under binary arches.` (dennis)
- add missing dependencies (nils)
- Fix checking optional ISO images in test phase (lsedlar)
- add lxml dependency (nils)
- images.json: Move src images under binary arches. (dmach)
- Add support for top-level variant IDs with dashes. (dmach)
- Fix PYTHONPATH usage in test_compose.sh. (dmach)
- [createiso] Enable customizing media reserve (lsedlar)
- [createiso] Add test for splitting media (lsedlar)
- [media-split] Remove commented-out code (lsedlar)
- [media-split] Simplify code (lsedlar)
- [media-split] Add code documentation (lsedlar)
- [media-split] Add unit tests (lsedlar)
- Add missing documentation (lsedlar)
- [buildinstall] Fix bad error message (lsedlar)
- Merge #309 `Add compatibility for Python 2.6` (dennis)
- Merge #293 `Add tests for generating discinfo and media.repo files` (dennis)
- Merge #287 `Use koji profiles to list RPMs in buildroot` (dennis)
- [ostree-installer] Put images to os/ directory (lsedlar)
- [ostree] Rename duplicated test (lsedlar)
- [util] Use koji profile for getting RPMs from buildroot (lsedlar)
- [util] Add test for getting list of buildroot RPMs (lsedlar)
- pungi-koji: fix up latest symlink creation (dennis)
- Use unittest2 if available (lsedlar)
- Stop using str.format (lsedlar)
- Stop using functools.total_ordering (lsedlar)
- The message attribute on exception is deprecated (lsedlar)
- [ostree] Rename duplicated test (lsedlar)
- [metadata] Simplify writing media.repo (lsedlar)
- [metadata] Add test for writing media.repo (lsedlar)
- [discinfo] Use context manager for file access (lsedlar)
- [metadata] Add tests for discinfo files (lsedlar)

* Tue May 24 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.6-1
- [ostree-installer] Allow using external repos as source (lsedlar)
- [image-build] Allow using external install trees (lsedlar)
- Add type to base product for layered releases (lsedlar)
- Merge #303 `[ostree] Use unique work and log paths` (dennis)
- [ostree] Use unique work and log paths (lsedlar)
- [arch] Add mock rpmUtils module (lsedlar)

* Mon May 16 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.5-1
- [ostree] Put variant name in ostree log dir (lsedlar)
- Merge #294 `[ostree] Initialize empty repo` (dennis)
- [util] Resolve git+https URLs (lsedlar)
- [ostree] Initialize empty repo (lsedlar)
- [test] Add checks for created images (lsedlar)
- Fix caching global ksurl (lsedlar)
- include tests/fixtures in manifest (dennis)

* Fri May 06 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.4-2
- add patch to fix caching global ksurl

* Fri Apr 29 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.4-1
- Merge #273 `Deduplicate configuration a bit` (dennis)
- Merge #280 `[createrepo] Use more verbose output` (dennis)
- Merge #283 `Pungi should log when it tries to publish notifications.`
>>>>>>> master
  (dennis)
- [createiso] Add back running isohybrid on x86 disk images (dennis)
- [createiso] Remove chdir() (lsedlar)
- [pkgset] Fix caching RPMs (lsedlar)
- [createrepo] Use more verbose output (lsedlar)
- Pungi should log when it tries to publish notifications. (rbean)
- [pkgset] Use context manager for opening file list (lsedlar)
- [pkgset] Add tests for writing filelists (lsedlar)
- [pkgset] Simplify finding RPM in koji buildroot (lsedlar)
- [pkgset] Clean up koji package set (lsedlar)
- [pkgset] Add test for pkgset merging (lsedlar)
- [pkgset] Add tests for KojiPackageSet (lsedlar)
- [pkgset] Clean up Koji source (lsedlar)
- [pkgset] Add tests for Koji source (lsedlar)
- Add common global settings for images (lsedlar)
- Remove duplicated and dead code (lsedlar)
- [live-media] Add check for live_media_version option (lsedlar)
- [scm-wrapper] Remove unused method (lsedlar)
- [scm-wrapper] Report when file wrapper did not match anything (lsedlar)
- [scm-wrapper] Use context manager for managing temp dir (lsedlar)
- [scm-wrapper] Reduce code duplication in RPM wrapper (lsedlar)
- [scm-wrapper] Copy files directly (lsedlar)
- [scm-wrapper] Reduce code duplication (lsedlar)
- [scm-wrapper] Add tests for SCM wrappers (lsedlar)
- [ostree] Set each repo to point to current compose (lsedlar)
- [ostree-installer] Drop filename setting (lsedlar)
- Merge #269 `Improve logging of failable deliverables` (ausil)
- [ostree-installer] Fix example documentation (lsedlar)
- Improve logging of failable deliverables (lsedlar)
- [ostree-installer] Install ostree in runroot (lsedlar)
- [pkgset] Print more detailed logs when rpm is not found (lsedlar)
- [ostree-installer] Clone repo with templates (lsedlar)

* Tue Apr 12 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.3-3
- add patch to install ostree in the ostree_installer runroot

* Mon Apr 11 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.3-2
- add patch to print more info for missing rpms
- add patch to clone repo with extra lorax templates for ostree_installer

* Fri Apr 08 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.3-1
- enable the compose test (dennis)
- [ostree-installer] Copy all lorax outputs (lsedlar)
- [ostree] Log to stdout as well (lsedlar)
- [ostree-installer] Use separate directory for logs (lsedlar)
- Merge #260 `Maybe fix ostree?` (ausil)
- [ostree-installer] Put lorax output into work dir (lsedlar)
- [ostree] Add test check for modified repo baseurl (lsedlar)
- [ostree] Move cloning repo back to compose box (lsedlar)
- [ostree] Mount ostree directory in koji (lsedlar)

* Thu Apr 07 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.2-2
- make sure that the shebang of pungi-pylorax-find-templates is python3

* Wed Apr 06 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.2-1
- Merge #257 `[ostree] Enable marking ostree phase as failable` (ausil)
- [ostree] Enable marking ostree phase as failable (lsedlar)
- [koji-wrapper] Initialize wrappers sequentially (lsedlar)
- [createiso] Simplify code, test phase (lsedlar)
- [createiso] Move runroot work to separate script (lsedlar)
- [ostree] Use explicit work directory (lsedlar)
- [ostree] Rename atomic to ostree (lsedlar)
- [ostree] Move cloning config repo to chroot (lsedlar)
- [ostree] Fix call to kobo.shortcuts.run (lsedlar)
- [atomic] Stop creating the os directory (lsedlar)
- [checksum] Add arch to file name (lsedlar)

* Tue Apr 05 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.1-3
- add some more ostree fixes
- add a bandaid for ppc until we get a proper fix

* Mon Apr 04 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.1-2
- add upstream patches for bugfixes in ostree and checksums

* Fri Apr 01 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.1-1
- install scripts (dennis)
- Merge #242 `Fix wrong file permissions` (ausil)
- Add a utility to validate config (lsedlar)
- [variants] Stop printing stuff to stderr unconditionally (lsedlar)
- Fix atomic/ostree config validations (lsedlar)
- [pungi-wrapper] Remove duplicated code (lsedlar)
- [checks] Add a check for too restrictive umask (lsedlar)
- [util] Remove umask manipulation from makedirs (lsedlar)
- Merge #240 `Filter variants and architectures` (ausil)
- Filter variants and architectures (lsedlar)
- Refactor checking for failable deliverables (lsedlar)
- [buildinstall] Do not crash on failure (lsedlar)
- Reuse helper in all tests (lsedlar)
- [atomic] Add atomic_installer phase (lsedlar)
- [ostree] Add ostree phase (lsedlar)
- [atomic] Add a script to create ostree repo (lsedlar)
- Merge #232 `Improve logging by adding subvariants` (ausil)
- Add compose type to release for images (lsedlar)
- [image-build] Add traceback on failure (lsedlar)
- [image-build] Use subvariants in logging output (lsedlar)
- [live-media] Use subvariants in logging (lsedlar)
- Add tracebacks to all failable phases (lsedlar)
- ppc no longer needs magic bits in the iso (pbrobinson)
- [buildinstall] Add more debugging output (lsedlar)
- [metadata] Stop crashing on empty path from .treeinfo (lsedlar)
- [checksums] Add label to file name (lsedlar)
- [buildinstall] Use customized dvd disc type (lsedlar)
- image_build: fix subvariant handling (awilliam)

* Fri Mar 11 2016 Dennis Gilmore <dennis@ausil.us> - 4.1.0-1
- upstream 4.1.0 release

* Thu Mar 10 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.9-2
- new tarball with upstream commits for test suite and pkgset

* Thu Mar 10 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.9-1
- [init] Update documentation (lsedlar)
- [init] Iterate over arches just once (lsedlar)
- [init] Remove duplicated checks for comps (lsedlar)
- [init] Break long lines (lsedlar)
- [init] Don't overwrite the same log file (lsedlar)
- [init] Add config option for keeping original comps (lsedlar)
- Add tests for the init phase (lsedlar)
- [checks] Test printing in all cases (lsedlar)
- [checks] Reduce code duplication (lsedlar)
- [checks] Relax check for genisoimage (lsedlar)
- [checks] Remove duplicate msgfmt line (lsedlar)
- [checks] Relax check for isohybrid command (lsedlar)
- [checks] Add tests for dependency checking (lsedlar)
- [checks] Don't always require jigdo (lsedlar)
- [pkgset] Respect inherit setting (lsedlar)
- specify that the 4.0 docs are for 4.0.8 (dennis)
- [live-media] Support release set to None globally (lsedlar)
- include tests/fixtures/* in the tarball (dennis)

* Wed Mar 09 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.8-2
- add patch to allow livemedia_release to be None globally

* Tue Mar 08 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.8-1
- Add README (lsedlar)
- [doc] Fix formatting (lsedlar)
- [createiso] Add customizing disc type (lsedlar)
- [live-images] Add customizing disc type (lsedlar)
- [buildinstall] Add customizing disc type (lsedlar)
- [buildinstall] Rename method to not mention symlinks (lsedlar)
- [gather] Fix documentation of multilib white- and blacklist (lsedlar)
- [paths] Document and test translate_path (lsedlar)
- [createrepo] Compute delta RPMS against old compose (lsedlar)
- [util] Add function to search for old composes (lsedlar)
- [live-media] Add global settings (lsedlar)
- [live-media] Rename test case (lsedlar)

* Thu Mar 03 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.7-1
- Limit the variants with config option 'tree_variants' (dennis)
- [createrepo-wrapper] Fix --deltas argument (lsedlar)
- [createrepo-wrapper] Add tests (lsedlar)
- [koji-wrapper] Retry watching on connection errors (lsedlar)
- [createrepo-wrapper] Refactor code (lsedlar)
- [paths] Use variant.uid explicitly (lsedlar)
- [createrepo] Add tests (lsedlar)
- [createrepo] Refactor code (lsedlar)
- [image-build] Fix resolving git urls (lsedlar)
- [testphase] Don't run repoclosure for empty variants (lsedlar)
- [live-images] No manifest for appliances (lsedlar)

* Fri Feb 26 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.6-1
- push the 4.0 docs to a 4.0 branch (dennis)
- [live-images] Rename log file (lsedlar)
- [buildinstall] Use -dvd- in volume ids instead of -boot- (lsedlar)
- [buildinstall] Hardlink boot isos (lsedlar)
- [doc] Write documentation for kickstart Git URLs (lsedlar)
- [util] Resolve branches in git urls (lsedlar)
- [live-images] Fix crash when repo_from is not a list (lsedlar)
- [buildinstall] Don't copy files for empty variants (lsedlar)

* Tue Feb 23 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.5-1
- [tests] Fix wrong checks in buildinstall tests (lsedlar)
- [tests] Use temporary files for buildinstall (lsedlar)
- [tests] Do not mock open for koji wrapper tests (lsedlar)
- Merge #179 `Update makefile targets for testing` (ausil)
- Update makefile targets for testing (lsedlar)
- [live-images] Set type to raw-xz for appliances (lsedlar)
- [live-images] Correctly create format (lsedlar)
- [tests] Dummy compose is no longer private (lsedlar)
- [tests] Move buildinstall tests to new infrastructure (lsedlar)
- [tests] Use real paths module in testing (lsedlar)
- [tests] Move dummy testing compose into separate module (lsedlar)
- [live-images] Create image dir if needed (lsedlar)
- [live-images] Add images to manifest (lsedlar)
- [live-images] Fix path processing (lsedlar)
- [live-images] Move repo calculation to separate method (lsedlar)
- [koji-wrapper] Fix getting results from spin-appliance (lsedlar)
- [live-images] Filter non-image results (lsedlar)
- [live-images] Rename repos_from to repo_from (lsedlar)
- [koji-wrapper] Add test for passing release to image-build (lsedlar)
- [live-images] Automatically populate release with date and respin (lsedlar)
- [live-media] Respect release set in configuration (lsedlar)
- [live-images] Build all images specified in config (lsedlar)
- [live-media] Don't create $basedir arch (lsedlar)
- Update tests (lsedlar)
- do not ad to image build and live tasks the variant if it is empty (dennis)
- when a variant is empty do not add it to the repolist for livemedia (dennis)
- [live-media] Update tests to use $basearch (lsedlar)
- [buildinstall] Don't run lorax for empty variants (lsedlar)
- Merge #159 `use $basearch not $arch in livemedia tasks` (lubomir.sedlar)
- Merge #158 `do not uses pipes.quotes in livemedia tasks` (lubomir.sedlar)
- Add documentation for signing support that was added by previous commit
  (tmlcoch)
- Support signing of rpm wrapped live images (tmlcoch)
- Fix terminology - Koji uses sigkey not level (tmlcoch)
- use $basearch not $arch in livemedia tasks (dennis)
- do not uses pipes.quotes in livemedia tasks (dennis)
- [live-images] Don't tweak kickstarts (lsedlar)
- Allow specifying empty variants (lsedlar)
- [createrepo] Remove dead assignments (lsedlar)
- Keep empty query string in resolved git url (lsedlar)
- [image-build] Use dashes as arch separator in log (lsedlar)
- [buildinstall] Stop parsing task_id (lsedlar)
- [koji-wrapper] Get task id from failed runroot (lsedlar)
- [live-media] Pass ksurl to koji (lsedlar)
- Merge #146 `[live-media] Properly calculate iso dir` (ausil)
- [live-media] Properly calculate iso dir (lsedlar)
- [image-build] Fix tests (lsedlar)
- add image-build sections (lkocman)
- [koji-wrapper] Add tests for get_create_image_cmd (lsedlar)
- [live-images] Add support for spin-appliance (lsedlar)
- [live-media] Koji option is ksfile, not kickstart (lsedlar)
- [live-media] Use install tree from another variant (lsedlar)
- [live-media] Put images into iso dir (lsedlar)
- [image-build] Koji expects arches as a comma separated string (lsedlar)
- Merge #139 `Log more details when any deliverable fails` (ausil)
- [live-media] Version is required argument (lsedlar)
- [koji-wrapper] Only parse output on success (lsedlar)
- [koji-wrapper] Add tests for runroot wrapper (lsedlar)
- [buildinstall] Improve logging (lsedlar)
- Log more details about failed deliverable (lsedlar)
- [image-build] Fix failable tests (lsedlar)
- Merge #135 `Add live media support` (ausil)
- Merge #133 `media_split: add logger support. Helps with debugging space
  issues on dvd media` (ausil)
- [live-media] Add live media phase (lsedlar)
- [koji-wrapper] Add support for spin-livemedia (lsedlar)
- [koji-wrapper] Use more descriptive method names (lsedlar)
- [image-build] Remove dead code (lsedlar)
- media_split: add logger support. Helps with debugging space issues on dvd
  media (lkocman)
- [image-build] Allow running image build scratch tasks (lsedlar)
- [image-build] Allow dynamic release for images (lsedlar)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.4-1
- 4.0.4 release (dennis)
- Merge #123 `Live images: add repo from another variant` (ausil)
- Merge #125 `[image-build] Stop creating wrong arch dirs` (ausil)
- Toggle multilib per variant (lsedlar)
- [live-images] Code cleanup (lsedlar)
- [live-images] Add documentation (lsedlar)
- [live-images] Add repos from other variants (lsedlar)
- [image-build] Stop creating wrong arch dirs (lsedlar)
- Enable identifying variants in exception traces (lsedlar)
- Store which deliverables failed (lsedlar)
- scm.py: use git clone instead git archive for http(s):// (lkocman)
- Fix filtering of system release packages (lsedlar)
- Merge #114 `Use install tree/repo from another variant for image build`
  (ausil)
- Make system release package filtering optional (lsedlar)
- [image-build] Optionally do not break whole compose (lsedlar)
- [image-build] Refactoring (lsedlar)
- [image-build] Use repo from another variant (lsedlar)
- [image-build] Take install tree from another variant (lsedlar)
- Add missing formats to volumeid and image name (lsedlar)
- [image-build] Use single koji task per variant (lsedlar)
- Fix image-build modifying config (lsedlar)
- Fix missing checksums in .treeinfo (lsedlar)
- Don't crash on generating volid without variant (lsedlar)
- Merge #99 `Add option to specify non-failing stuff` (ausil)
- Add repo from current compose (lsedlar)
- Fix getting compose topdir in CreateImage build thread (lsedlar)
- Add option to specify non-failing stuff (lsedlar)
- Allow customizing image name and volume id (lsedlar)
- Fix notifier tests (lsedlar)
- Publish a url instead of a file path. (rbean)
- Add 'topdir' to all fedmsg/notifier messages. (rbean)
- Merge #75 `Start of development guide` (ausil)
- Merge #88 `Resolve HEAD in ksurl to actual hash` (ausil)
- Merge #87 `Add support for customizing lorax options` (ausil)
- Update fedmsg notification hook to use appropriate config. (rbean)
- we need to ensure that we send all the tasks to koji on the correct arch
  (dennis)
- Resolve HEAD in ksurl to actual hash (lsedlar)
- Add support for customizing lorax options (lsedlar)
- Run lorax in separate dirs for each variant (lsedlar)
- Merge #84 `Allow specifying --installpkgs for lorax` (ausil)
- Merge #83 `Fix recently discovered bugs` (ausil)
- Merge #82 `indentation fixs correcting dvd creation` (ausil)
- Merge #69 `Move messaging into cli options and simplify it` (ausil)
- Start lorax for each variant separately (lsedlar)
- Update lorax wrapper to use --installpkgs (lsedlar)
- Allow specifying which packages to install in variants xml (lsedlar)
- Add basic tests for buildinstall phase (lsedlar)
- Fix generating checksum files (lsedlar)
- Use lowercase hashed directories (lsedlar)
- indentation fixs correcting dvd creation (dennis)
- remove glibc32 from the runroot tasks (dennis)
- fix up the pungi-fedmesg-notification script name (dennis)
- Add overview of Pungi to documentation (lsedlar)
- Move messaging into cli options (lsedlar)
- Extend contributing guide (lsedlar)
- Load multilib configuration from local dir in development (lsedlar)
- Allow running scripts with any python in PATH (lsedlar)

* Tue Sep 08 2015 Dennis Gilmore <dennis@ausil.us> 4.0.3-1
- Merge #54 `fix log_info for image_build (fails if image_build is skipped)`
  (lkocman)
- image_build: self.log_info -> self.compose.log_info (lkocman)
- Revert "Added params needed for Atomic compose to LoraxWrapper" (dennis)
- Revert "fix up if/elif in _handle_optional_arg_type" (dennis)
- Add image-build support (lkocman)
- Add translate path support. Useful for passing pungi repos to image-build
  (lkocman)
- import duplicate import of errno from buildinstall (lkocman)
- handle openning missing images.json (image-less compose re-run) (lkocman)
- compose: Add compose_label_major_version(). (lkocman)
- pungi-koji: Don't print traceback if error occurred. (pbabinca)
- More detailed message for unsigned rpms. (tkopecek)
- New config option: product_type (default is 'ga'); Set to 'updates' for
  updates composes. (dmach)
- kojiwrapper: Add get_signed_wrapped_rpms_paths() and get_build_nvrs()
  methods. (tmlcoch)
- live_images: Copy built wrapped rpms from koji into compose. (tmlcoch)
- kojiwrapper: Add get_wrapped_rpm_path() function. (tmlcoch)
- live_images: Allow custom name prefix for live ISOs. (tmlcoch)
- Do not require enabled runroot option for live_images phase. (tmlcoch)
- Support for rpm wrapped live images. (tmlcoch)
- Remove redundant line in variants wrapper. (tmlcoch)
- Merge #36 `Add params needed for Atomic compose to LoraxWrapper` (admiller)
- live_images: replace hardcoded path substition with translate_path() call
  (lkocman)
- live_images fix reference from koji to koji_wrapper (lkocman)
- fix up if/elif in _handle_optional_arg_type (admiller)
- Added params needed for Atomic compose to LoraxWrapper (admiller)
- Merge #24 `Fix empty repodata when hash directories were enabled. ` (dmach)
- createrepo: Fix empty repodata when hash directories were enabled. (dmach)

* Fri Jul 24 2015 Dennis Gilmore <dennis@ausil.us> - 4.0.2-1
- Merge #23 `fix treeinfo checksums` (dmach)
- Fix treeinfo checksums. (dmach)
- add basic setup for making arm iso's (dennis)
- gather: Implement hashed directories. (dmach)
- createiso: Add createiso_skip options to skip createiso on any variant/arch.
  (dmach)
- Fix buildinstall for armhfp. (dmach)
- Fix and document productimg phase. (dmach)
- Add armhfp arch tests. (dmach)
- Document configuration options. (dmach)
- Add dependency of 'runroot' config option on 'koji_profile'. (dmach)
- Rename product_* to release_*. (dmach)
- Implement koji profiles. (dmach)
- Drop repoclosure-%%arch tests. (dmach)
- Config option create_optional_isos now defaults to False. (dmach)
- Change createrepo config options defaults. (dmach)
- Rewrite documentation to Sphinx. (dmach)
- Fix test data, improve Makefile. (dmach)
- Update GPL to latest version from https://www.gnu.org/licenses/gpl-2.0.txt
  (dmach)

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Dennis Gilmore <dennis@ausil.us> - 4.0.1-1
- wrap check for selinux enforcing in a try except (dennis)
- pull in gather.py patches from dmach for test compose (admiller)
- Add some basic testing, dummy rpm creation, and a testing README (admiller)
- pungi-koji: use logger instead of print when it's available (lkocman)
- fix incorrect reference to variable 'product_is_layered' (lkocman)
- pungi-koji: fix bad module path to verify_label() (lkocman)
- update the package Requires to ensure we have everything installed to run
  pungi-koji (dennis)
- update the package to be installed for productmd to python-productmd (dennis)

* Sun Jun 07 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.9.20150607.gitef7c78c
- update docs now devel-4-pungi is merged to master, minor spelling fixes
  (pbrobinson)
- Fix remaining productmd issues. (dmach)
- Revert "refactor metadata.py to use productmd's compose.dump for composeinfo"
  (dmach)
- Fix LoraxTreeInfo class inheritance. (dmach)
- Fix pungi -> pungi_wrapper namespace issue. (dmach)
- fix arg order for checksums.add (admiller)
- update for productmd checksums.add to TreeInfo (admiller)
- fix product -> release namespace change for productmd (admiller)
- update arch manifest.add config order for productmd api call (admiller)
- update for new productmd named args to rpms (admiller)
- fix pungi vs pungi_wrapper namespacing in method_deps.py (admiller)
- add createrepo_c Requires to pungi.spec (admiller)
- add comps_filter (admiller)
- refactor metadata.py to use productmd's compose.dump for composeinfo instead
  of pungi compose_to_composeinfo (admiller)
- Update compose, phases{buildinstall,createiso,gather/__ini__} to use correct
  productmd API calls (admiller)
- Use libselinux-python instead of subprocess (lmacken)
- Add README for contributors (admiller)

* Wed May 20 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.8.20150520.gitff77a92
- fix up bad += from early test of implementing different iso labels based on
  if there is a variant or not (dennis)

* Wed May 20 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.7.20150520.gitdc1be3e
- make sure we treat the isfinal option as a boolean when fetching it (dennis)
- if there is a variant use it in the volume id and shorten it. this will make
  each producst install tree have different volume ids for their isos (dennis)
- fix up productmd import in the executable (dennis)
- fixup productmd imports for changes with open sourcing (dennis)
- tell the scm wrapper to do an absolute import otherwise we hit a circular dep
  issue and things go wonky (dennis)
- include the dtd files in /usr/share/pungi (dennis)
- add missing ) causing a syntax error (dennis)
- fix up the productmd imports to import the function from the common module
  (dennis)
- fix up typo in getting arch for the lorax log file (dennis)

* Sat Mar 14 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.6.20150314.gitd337c34
- update the git snapshot to pick up some fixes

* Fri Mar 13 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.5.git18d4d2e
- update Requires for rename of python-productmd

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.4.git18d4d2e
- fix up the pungi logging by putting the arch in the log file name (dennis)
- change pypungi imports to pungi (dennis)
- spec file cleanups (dennis)

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.3.gita3158ec
- rename binaries (dennis)
- Add the option to pass a custom path for the multilib config files (bcl)
- Call lorax as a process not a library (bcl)
- Close child fds when using subprocess (bcl)
- fixup setup.py and MANIFEST.in to make a useable tarball (dennis)
- switch to BSD style hashes for the iso checksums (dennis)
- refactor to get better data into .treeinfo (dennis)
- Initial code merge for Pungi 4.0. (dmach)
- Initial changes for Pungi 4.0. (dmach)
- Add --nomacboot option (csieh)

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.2.git320724e
- update git snapshot to switch to executing lorax since it is using dnf

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.1.git64b6c80
- update to the pungi 4.0 dev branch

* Mon Dec 15 2014 Dennis Gilmore <dennis@ausil.us> - 3.12-3
- add patch to make the dvd bootable on aarch64

* Tue Sep 30 2014 Dennis Gilmore <dennis@ausil.us> - 3.12-2
- add patch to fix whitespace errors

* Thu Sep 11 2014 Dennis Gilmore <dennis@ausil.us> - 3.12-1
- Remove magic parameter to mkisofs (hamzy)
- Added option for setting release note files (riehecky)

* Thu Jul 31 2014 Dennis Gilmore <dennis@ausil.us> - 3.11-1
- make sure that the dvd/cd is using the shortened volumeid (dennis)

* Thu Jul 31 2014 Dennis Gilmore <dennis@ausil.us> - 3.10-1
- fix up volume shortening substituions to actually work (dennis)

* Wed Jul 30 2014 Dennis Gilmore <dennis@ausil.us> - 3.09-1
- implement nameing scheme from
  https://fedoraproject.org/wiki/User:Adamwill/Draft_fedora_image_naming_policy
