# Copyright (C) 2012 Tresys Technology, LLC
# Copyright (C) 2014 Quark Security, Inc
#
# Authors: Spencer Shimko <sshimko@tresys.com>
# 	   Spencer Shimko <spencer@quarksecurity.com>
#

# The name of the package
PKGNAME := clip-selinux-policy

# These two are typically set by the top-level CONFIG_BUILD file.
BUILD_CONFIG_ENFORCING_MODE ?= y
BUILD_CONFIG_TOOR ?= n

# This is the version number of the RPM that will be
# generated.  Typically you bump this for delivery.
VERSION := 6.5.0

# bump this if creating multiple releases from the same
# version (think about this... why are you doing this?)
RELEASE := 1

# The name of the Vendor
VENDOR := Quark Security, Inc 

# The name of the Packager
PACKAGER ?= Quark Security, Inc

# snag the architecture, hard code an arch if cross-compiling or going noarch
ARCH ?= noarch

# Policy modules listed here will be built as separate RPMs
# e.g., clip-selinux-policy-apache
SEPARATE_PKGS := aide apache mysql postfix samhain ssh tripwire unprivuser

# the filename of the tarball
TARBALL = $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION).tar.gz

# spec file name
RPM_SPEC = $(CURDIR)/$(PKGNAME).spec

####################################################
## things below this line should rarely change
ROOT_DIR ?= $(CURDIR)
OUTPUT_DIR ?= $(ROOT_DIR)
SRPM_OUTPUT_DIR ?= $(OUTPUT_DIR)

# exhaustive list of deps for the RPM, used to determine if RPM needs to be rebuilt
TAR_DEPS := $(shell find $(PKGNAME)/)
RPM_DEPS := $(TARBALL) $(RPM_SPEC) $(CURDIR)/Makefile

RPM_TMPDIR ?= $(ROOT_DIR)/tmp
RPM_TOPDIR ?= $(RPM_TMPDIR)/src/redhat
RPM_BUILDROOT ?= $(RPM_TMPDIR)/rpm-buildroot

MKDIR = test -d $(1) || mkdir -p $(1)

RPMBUILD_ARGS := --define '_topdir $(RPM_TOPDIR)'  --define '_tmppath $(RPM_TMPDIR)' --buildroot $(RPM_BUILDROOT)

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
	ENFORCING_MODE := enforcing
else
	ENFORCING_MODE := permissive
endif
ifneq ($(CONFIG_BUILD_UNCONFINED_TOOR),n)
	ENABLE_MODULES += toor
endif

ifeq ($(SEPARATE_PKGS),)
SEPARATE_PKGS := %{nil}
else
ENABLE_MODULES += $(SEPARATE_PKGS)
endif

ifeq ($(ENABLE_MODULES),)
ENABLE_MODULES := %{nil}
endif

RPMQ_DEFS := --query --define 'separatePkgs $(SEPARATE_PKGS)' --define 'pkgname $(PKGNAME)' --define '_sysconfdir /etc' --define 'version $(VERSION)' --define 'release $(RELEASE)' --define 'vendor $(VENDOR)' --define 'packager $(PACKAGER)' --qf '%{NAME}\n'

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
	cp $(TARBALL) $(RPM_TOPDIR)/SOURCES/
	echo -e "%define enable_modules $(ENABLE_MODULES)\n%define enforcing_mode $(ENFORCING_MODE)\n%define pkgname $(PKGNAME)\n%define _sysconfdir /etc\n%define version $(VERSION)\n%define release $(RELEASE)\n%define vendor $(VENDOR)\n%define packager $(PACKAGER)\nBuildArch: $(ARCH)\n%define separatePkgs $(SEPARATE_PKGS)\n"> $(RPM_TOPDIR)/SPECS/$(notdir $(RPM_SPEC))
	cat $(RPM_SPEC) >> $(RPM_TOPDIR)/SPECS/$(notdir $(RPM_SPEC))
	cd $(RPM_TOPDIR) && rpmbuild $(RPMBUILD_ARGS) -bs SPECS/$(notdir $(RPM_SPEC)) --nodeps
	mv  $(RPM_TOPDIR)/SRPMS/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm $(SRPM_OUTPUT_DIR)

clean:
	$(RM) -r $(RPM_TMPDIR)

bare: clean
	$(foreach f,$(shell rpm $(RPMQ_DEFS) --specfile $(RPM_SPEC)),$(RM) $(OUTPUT_DIR)/$(f)*.rpm;)
	$(RM) $(TARBALL) $(SRPM_OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).src.rpm $(OUTPUT_DIR)/$(PKGNAME)-$(VERSION)-$(RELEASE).$(ARCH).rpm

.PHONY: all rpm srpm $(PKGNAME)-rpm $(PKGNAME)-srpm clean bare
