# Copyright (C) 2012 Tresys Technology, LLC
# Copyright (C) 2014-15 Quark Security, Inc
# Copyright (C) 2023 Sealing Technologies, Inc.
#
# Authors: Spencer Shimko <sshimko@tresys.com>
# 	   Spencer Shimko <spencer@quarksecurity.com>
# 	   Spencer Shimko <spencer@sealingtech.com>
#
#
#
# NOTE: you can override any of the config variables in a Makefile.supl
# except the SEPARATE_PKGS feature that splits policy mods into separate i
# RPMs. The list is added to the list defined below in this file.
# You can disable that behavior and disable all of the SEPARATE_PKGS 
# added in this Makefile by setting "DISABLE_STD_SEPARATE_PKGS := y"
-include $(CURDIR)/Makefile.supl

# The name of the package
PKGNAME ?= selinux-policy

# These two are typically set by the top-level CONFIG_BUILD file.
CONFIG_BUILD_ENFORCING_MODE ?= y
CONFIG_BUILD_TOOR ?= n


# This is the version number of the RPM that will be
# generated.  Typically you bump this for delivery.
ifdef DEVVER
VERSION ?= 999.1.$(DEVVER)
else
VERSION ?= 999.1
endif

# bump this if creating multiple releases from the same
# version (think about this... why are you doing this?)
RELEASE ?= el8

# The name of the Vendor
VENDOR ?= Sealing Technologies, Inc.

# The name of the Packager
PACKAGER ?= Sealing Technologies, Inc.

# snag the architecture, hard code an arch if cross-compiling or going noarch
ARCH := noarch

# Specify the type of policy to build.
# This _will_ override the TYPE= value in build.conf
# Currently either mcs, mls, or standard.
# Only supported for CIL builds at the moment (RHEL 7.3 and some later 7.2.x releases).
CONFIG_BUILD_SELINUX_POL_TYPE ?= mcs

ifneq ($(DISABLE_STD_SEPARATE_PKGS),y)
# SELinux policy supports building individual policy components in a modular manner.
# This is typically controlled by modifying selinux-policy/policy/modules.conf.
#
# The vendor packages isntall nearly all of those built as "modules" from the main
# selinux-policy-TYPE RPM and enables them all by default. You can end up with a lot
# to disable with that approach.
#
# First, CLIP includes a very trimmed down set of enabled modules in modules.conf,
# and then adds the following feature...
#
# CLIP supports building policy packages (pp) files and placing them in separate RPMs
# to ease development (e.g., install specific packages to aid development, but don't
# install them in production builds) and building for multiple system types from one
# policy tree.
#
# A number of modules are includes in the main selinux-policy-TYPE RPM that
# are pretty much necessary for system functionality.
# Policy modules listed here will be built as separate RPMs.
# e.g., selinux-policy-mcs-apache will install the apache.pp policy package.
#
# Listing a module here will also cause it to be enabled even if it
# disabled in modules.conf.
#
# SSH is a perfect example of a module that would be present during development,
# but not necessairly once a system is deployed.
SEPARATE_PKGS += ssh

# These system components are typically installed by default even in minimal installs and you have to manually remove them
SEPARATE_PKGS += rhsmcertd oddjob rtkit

# security guides install these even if you don't want them, but in case you're ignoring those guides just don't install the RPMs
SEPARATE_PKGS += aide postfix usbguard fapolicyd rngd

# Common roles.
# By default, we have staff and sysadm built into the core policy RPM.
# If you are developing for an embedded, maybe you don't want any roles except during dev, in which case put them all here.
# IF YOU PUT ALL ROLES IN SEPARATE RPMs MAKE SURE YOU INSTALL THE RPMs FOR THE ROLES YOU WANT OR LOGINS WON'T WORK!
SEPARATE_PKGS +=  logadm auditadm secadm # staff sysadm unprivuser

# Auth-related
SEPARATE_PKGS += sasl rpcbind rpc gssproxy kerberos certmonger pcscd

# Got UPS?
SEPARATE_PKGS += apcupsd nut

# A few random services we have used in either CLIP variants or we wsee being commonly deployed by systems using this policy
SEPARATE_PKGS += postgresql mysql apache bind openvpn samba denyhosts ntp

# These are pretty much necessary for typical GUI support
SEPARATE_PKGS += xserver accountsd colord geoclue gnome wm telepathy bluetooth devicekit consolekit
endif # ifneq DISABLE_STD_SEPARATE_PKGS,y

# Since the policy structure changes between 7.2 and 7.3, we need to decide which spec to use
# <3 awk
ifeq ($(OS_REL),)
override OS_REL ?= 8.6
endif

# Yes, use awk to perform floating point math. Believe it or not, bc is not installed by default and bash only does integer math and make doesn't have a clean way to do it.
SPEC_VER := $(strip $(shell awk 'BEGIN { print ($(OS_REL) >= 7.3) ? "-cil" : "-nocil"; }'))
# version-specific spec file name
RPM_V_SPEC = $(CURDIR)/$(PKGNAME)$(SPEC_VER).spec
RPM_SPEC = $(RPM_TOPDIR)/SPECS/$(PKGNAME).spec

####################################################
## things below this line should rarely change
ROOT_DIR ?= $(CURDIR)
OUTPUT_DIR ?= $(ROOT_DIR)
SRPM_OUTPUT_DIR ?= $(OUTPUT_DIR)

# the filename of the tarball
TARBALL = $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION).tar.gz

# Other source files rolled into the src.rpm
SOURCES := support/Makefile.devel support/rpm.macros support/macro-expander support/selinux-policy.conf

# exhaustive list of deps for the RPM, used to determine if RPM needs to be rebuilt
TAR_DEPS := $(CURDIR)/Makefile $(shell find $(CURDIR)/$(PKGNAME)/* -type f -or -type d | sed -e "s/ /\\\ /g")
RPM_DEPS = $(TARBALL) $(SOURCES) $(RPM_V_SPEC) $(CURDIR)/Makefile $(ADDTL_DEPS)

RPM_TMPDIR ?= $(ROOT_DIR)/tmp
RPM_TOPDIR ?= $(RPM_TMPDIR)/src/redhat
RPM_BUILDROOT ?= $(RPM_TMPDIR)/rpm-buildroot

MKDIR = test -d $(1) || mkdir -p $(1)

RPMBUILD_ARGS := --define '_topdir $(RPM_TOPDIR)'  --define '_tmppath $(RPM_TMPDIR)' --buildroot $(RPM_BUILDROOT)

# this hack is because I can not figure out hot the heck to get rpm query to expand a variable defined in a spec file.
# --eval only expxands built-in macros and eval %dump is no help either.
# In short, since we need to rebuild the src RPM whenever the OS_REL changes, we need to remove the spec file
ifeq ($(strip $(shell test -f $(RPM_SPEC) && grep "OS_REL $(OS_REL)" $(RPM_SPEC))),)
$(shell rm -f $(RPM_SPEC))
$(shell rm -f $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm)
endif

# FIXME: This and the shell above can probably be fixed by extract the spec from the src rpm
# and looking at that spec for the value.
# For now assume that if we don't have a spec file to analyze remove the srpm.
$(shell test -f $(RPM_SPEC) ||  rm -f $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm)

define rpm-prep
	$(call MKDIR,$(RPM_TOPDIR)/SOURCES)
	$(call MKDIR,$(RPM_TOPDIR)/SPECS)
	$(call MKDIR,$(RPM_TOPDIR)/BUILD)
	$(call MKDIR,$(RPM_TOPDIR)/RPMS/$(ARCH))
	$(call MKDIR,$(RPM_TOPDIR)/SRPMS)
endef


# Note: due to remediation content, overriding this may not work the way you expect.
# Look at the bottom of the stock clip-rhel6--ks %post for an example.
ifneq ($(CONFIG_BUILD_ENFORCING_MODE),n)
	ENFORCING_MODE ?= enforcing
else
	ENFORCING_MODE ?= permissive
endif

# always build toor as a separate RPM.
# include or exclude by adding or removing
# selinux-policy-$(CONFIG_BUILD_SELINUX_POL_TYPE)-toor
# from the kickstart, or in kickstart/includes/standard-packages.
#SEPARATE_PKGS += toor

ENABLE_MODULES := $(ENABLE_MODULES) $(SEPARATE_PKGS)

ifeq ($(strip $(SEPARATE_PKGS)),)
SEPARATE_PKGS := %{nil}
endif

ifeq ($(strip $(ENABLE_MODULES)),)
ENABLE_MODULES := %{nil}
endif

RPMQ_DEFS := --query --define 'separatePkgs $(SEPARATE_PKGS)' --define 'type $(CONFIG_BUILD_SELINUX_POL_TYPE)' --define 'pkgname $(PKGNAME)' --define '_sysconfdir /etc' --define 'version $(VERSION)' --define 'release $(RELEASE)' --define 'vendor $(VENDOR)' --define 'packager $(PACKAGER)' --qf '%{NAME}\n'

all: $(PKGNAME)-rpm $(PKGNAME)-srpm

rpm: $(PKGNAME)-rpm

srpm: $(PKGNAME)-srpm

$(PKGNAME)-rpm: $(OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).$(ARCH).rpm

$(PKGNAME)-srpm: $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm

$(TARBALL): $(TAR_DEPS)
	@echo "Building $(PKGNAME) source tarball..."
	tar -czf $@ $(PKGNAME)/

$(OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).$(ARCH).rpm: $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm
	@echo "Building $(PKGNAME) RPM..."
	$(call rpm-prep)
	cd $(RPM_TOPDIR)/SRPMS && rpmbuild --rebuild --target=$(ARCH) $(RPMBUILD_ARGS) --buildroot $(RPM_BUILDROOT) -bb $<
	if [ $(ARCH) != "noarch" ]; then cp $(RPM_TOPDIR)/RPMS/noarch/* $(OUTPUT_DIR)/ 2>&1 >/dev/null; exit 0; fi
	mv  $(RPM_TOPDIR)/RPMS/$(ARCH)/*.rpm $(OUTPUT_DIR)

$(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm: $(RPM_DEPS)
	@echo "Building $(PKGNAME) SRPM..."
	$(call rpm-prep)
	cp $(SOURCES) $(TARBALL) $(RPM_TOPDIR)/SOURCES/
	echo -e "%define type $(CONFIG_BUILD_SELINUX_POL_TYPE)\n%define enable_modules $(ENABLE_MODULES)\n%define enforcing_mode $(ENFORCING_MODE)\n%define pkgname $(PKGNAME)\n%define _sysconfdir /etc\n%define version $(VERSION)\n%define release $(RELEASE)\n%define vendor $(VENDOR)\n%define packager $(PACKAGER)\nBuildArch: $(ARCH)\n%define separatePkgs $(SEPARATE_PKGS)\n%define OS_REL $(OS_REL)\n"> $(RPM_SPEC)
	cat $(RPM_V_SPEC) >> $(RPM_SPEC)
	cd $(RPM_TOPDIR) && rpmbuild $(RPMBUILD_ARGS) -bs $(RPM_SPEC) --nodeps
	mv  $(RPM_TOPDIR)/SRPMS/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm $(SRPM_OUTPUT_DIR)

clean:
	$(RM) -r $(RPM_TMPDIR)

bare: clean
	$(foreach f,$(shell rpm $(RPMQ_DEFS) --specfile $(RPM_V_SPEC) > /dev/null),$(RM) $(OUTPUT_DIR)/$(f)*.rpm > /dev/null;)
	$(RM) $(TARBALL) $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm $(OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).$(ARCH).rpm
	@[[ "$(DEVVER)" != "" ]] && /bin/echo -e "WARNING: DEVVER variable set to $(DEVVER) in $(CURDIR)/Makefile, $(CURDIR)/Makefile.supl, or on the command-line.\nWARNING: Often this is a build-time timestamp. The source tarball and All RPMs might not have been removed.\n"; true

.PHONY: all rpm srpm $(PKGNAME)-rpm $(PKGNAME)-srpm clean bare
