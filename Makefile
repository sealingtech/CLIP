# Copyright (C) 2011-2012 Tresys Technology, LLC
# Copyright (C) 2011-2015 Quark Security, Inc
# Copyright (C) 2013 Cubic Corporation
# 
# Authors: Spencer Shimko <sshimko@tresys.com>
#          Spencer Shimko <spencer@quarksecurity.com>
#	   John Feehley <jfeehley@quarksecurity.com>
#
# Typically a user of CLIP does not have to modify this file.
# See CONFIG_BUILD for configuration options
# See CONFIG_REPOS to setup yum repos


######################################################
# Import build config (version, release, repos, etc)
include CONFIG_BUILD
-include CONFIG_AWS

# This is the RHEL version supported by this release of CLIP.  Do not alter.
export RHEL_VER := 6

######################################################
# BEGIN MAGIC
ifneq ($(QUIET),y)
$(info Boot strapping build system...)
endif

# NOTE: DO NOT REMOVE THIS CHECK. RUNNING MOCK AS ROOT *WILL* BREAK THINGS.
ifeq ($(shell id -u),0)
$(error Never CLIP as root! It will break things!  Try again as an unprivileged user with sudo access.)
endif

HOST_RPM_DEPS := rpm-build createrepo mock repoview

export ROOT_DIR ?= $(CURDIR)
export OUTPUT_DIR ?= $(ROOT_DIR)
export RPM_TMPDIR ?= $(ROOT_DIR)/tmp
export CONF_DIR ?= $(ROOT_DIR)/conf
export TOOLS_DIR ?= $(ROOT_DIR)/tmp/tools
export LIVECD_VERSION ?= $(shell rpm --eval `sed -n -e 's/Release: \(.*\)/\1/p' -e 's/Version: \(.*\)/\1/p' \
                 packages/livecd-tools/livecd-tools.spec| sed 'N;s/\n/-/'`)

export PUNGI_VERSION ?= 2.0.22-1

# Config deps
CONFIG_BUILD_DEPS := $(ROOT_DIR)/CONFIG_BUILD $(ROOT_DIR)/CONFIG_REPOS $(ROOT_DIR)/Makefile $(CONF_DIR)/pkglist.blacklist

# MOCK_REL must be configured in MOCK_CONF_DIR/MOCK_REL.cfg
MOCK_REL := rhel-$(RHEL_VER)-$(TARGET_ARCH)

# This directory contains all of our packages we will be building.
PKG_DIR += $(CURDIR)/packages

#determine which variants we're building
VARIANTS := $(filter %-inst-iso %-live-iso %-aws-ami,$(MAKECMDGOALS))
VARIANTS := $(subst -inst-iso,,$(VARIANTS))
VARIANTS := $(subst -aws-ami,,$(VARIANTS))
VARIANTS := $(subst -live-iso,,$(VARIANTS))
ifeq ($(strip $(VARIANTS)),)
PACKAGES := $(shell ls $(PKG_DIR) | grep -v examples)
else
$(foreach VARIANT,$(VARIANTS), $(eval include kickstart/$(VARIANT)/variant_pkgs.mk))
endif

ifeq ($(CONFIG_BUILD_ENABLE_SSH_6),n)
PACKAGES := $(filter-out openssh-six,$(PACKAGES))
endif

# This is the directory that will contain all of our yum repos.
REPO_DIR := $(CURDIR)/repos

# This directory contains images files, the Makefiles, and other files needed for ISO generation
KICKSTART_DIR := $(CURDIR)/kickstart

# Files supporting the build process
SUPPORT_DIR := $(CURDIR)/support

# mock will be used to build the packages in a clean environment.
MOCK_CONF_DIR := $(CONF_DIR)/mock

# we need a yum.conf to use for repo querying (to determine appropriate package versions when multiple version are present)
YUM_CONF_FILE := $(CONF_DIR)/yum/yum.conf
export YUM_CONF_ALL_FILE := $(CONF_DIR)/yum/yum_all.conf

# Pungi needs a comps.xml - why does every single yum front-end suck in different ways?
COMPS_FILE := $(CONF_DIR)/yum/comps.xml

export EC2_AMI_TOOLS := $(RPM_TMPDIR)/ec2-ami-tools
EC2_AMI_TOOLS_ZIP    := $(RPM_TMPDIR)/ec2-ami-tools.zip
EC2_AMI_TOOLS_URL    := http://s3.amazonaws.com/ec2-downloads/ec2-ami-tools.zip

ifeq ($(AWS_AVAIL_ZONE),us-east-1)
export AWS_KERNEL    ?= aki-919dcaf8
else ifeq ($(AWS_AVAIL_ZONE),us-west-1)
export AWS_KERNEL    ?= aki-880531cd
else ifeq ($(AWS_AVAIL_ZONE),us-west-2)
export AWS_KERNEL    ?= aki-fc8f11cc
else ifeq ($(AWS_AVAIL_ZONE),eu-west-1)
export AWS_KERNEL    ?= aki-52a34525
else ifeq ($(AWS_AVAIL_ZONE),eu-central-1)
export AWS_KERNEL    ?= aki-184c7a05
else ifeq ($(AWS_AVAIL_ZONE),ap-southeast-1)
export AWS_KERNEL    ?= aki-503e7402
else ifeq ($(AWS_AVAIL_ZONE),ap-southeast-2)
export AWS_KERNEL    ?= aki-c362fff9
else ifeq ($(AWS_AVAIL_ZONE),ap-northeast-1)
export AWS_KERNEL    ?= aki-176bf516
else ifeq ($(AWS_AVAIL_ZONE),sa-east-1)
export AWS_KERNEL    ?= aki-5553f448
endif
export AWS_AVAIL_ZONE

export EC2_API_TOOLS := $(RPM_TMPDIR)/ec2-api-tools
EC2_API_TOOLS_ZIP    := $(RPM_TMPDIR)/ec2-api-tools.zip
EC2_API_TOOLS_URL    := http://s3.amazonaws.com/ec2-downloads/ec2-api-tools.zip

export MOCK_YUM_CONF :=
export setup_all_repos := setup-clip-repo
CLIP_REPO_DIRS :=

# These are the directories where we will put our custom copies of
# the yum repos.  These will be removed by "make bare".
CLIP_REPO_DIR := $(REPO_DIR)/clip-repo
CLIP_SRPM_REPO_DIR := $(REPO_DIR)/clip-srpms
export REPO_LINES := repo --name=clip-repo --baseurl=file://$(CLIP_REPO_DIR)\n

export SRPM_OUTPUT_DIR := $(CLIP_SRPM_REPO_DIR)

export MAYFLOWER := $(SUPPORT_DIR)/mayflower

SED := /bin/sed
GREP := /bin/egrep
MOCK := /usr/bin/mock
REPO_LINK := /bin/ln -s
REPO_WGET := /usr/bin/wget
REPO_CREATE := /usr/bin/createrepo -d --workers $(shell /usr/bin/nproc) -c $(REPO_DIR)/yumcache
REPO_QUERY = repoquery -c $(1) --quiet -a --queryformat '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm'
MOCK_ARGS += --resultdir=$(CLIP_REPO_DIR) -r $(MOCK_REL) --configdir=$(MOCK_CONF_DIR) --unpriv --rebuild

# This deps list gets propegated down to sub-makefiles
# Add to this list to pass deps down to SRPM creation
export SRPM_DEPS := $(CONFIG_BUILD_DEPS)

PKG_BLACKLIST := $(shell $(SED) -e 's/\(.*\)\#.*/\1/g' $(CONF_DIR)/pkglist.blacklist|$(SED) -e ':a;N;$$!ba;s/\n/ /g')

# Macros to determine package info: version, release, arch.
PKG_VER = $(strip $(eval $(shell $(GREP) ^VERSION $(PKG_DIR)/$(1)/Makefile))$(VERSION))
PKG_REL = $(strip $(eval $(shell $(GREP) ^RELEASE $(PKG_DIR)/$(1)/Makefile))$(RELEASE))
PKG_ARCH = $(strip $(eval $(shell $(GREP) ^ARCH $(PKG_DIR)/$(1)/Makefile))$(ARCH))
# macros for converting between package name and file names
RPM_FROM_PKG_NAME = $(1)-$(call PKG_VER,$(1))-$(call PKG_REL,$(1)).$(call PKG_ARCH,$(1)).rpm
SRPM_FROM_PKG_NAME = $(1)-$(call PKG_VER,$(1))-$(call PKG_REL,$(1)).src.rpm
PKG_NAME_FROM_RPM = $(shell echo "$(1)" | $(SED) -r -e 's/^([^-]+[A-Za-z_-]?+)-.*$$/\1/')
SRPM_FROM_RPM = $(patsubst %.$(call PKG_ARCH,$(call PKG_NAME_FROM_RPM,$(1))).rpm,%.src.rpm,$(1))

# Create the list of RPMs based on package list.
RPMS := $(addprefix $(CLIP_REPO_DIR)/,$(foreach PKG,$(PACKAGES),$(call RPM_FROM_PKG_NAME,$(strip $(PKG)))))
SRPMS := $(addprefix $(SRPM_OUTPUT_DIR)/,$(foreach RPM,$(RPMS),$(call SRPM_FROM_RPM,$(notdir $(RPM)))))

ifeq ($(QUIET),y)
	VERBOSE = @
endif

MKDIR = $(VERBOSE)test -d $(1) || mkdir -p $(1)

SYSTEMS := $(shell find $(KICKSTART_DIR) -maxdepth 1 ! -name kickstart -type d -printf "%f\n")

# These are targets supported by the kickstart/Makefile that will be used to generate LiveCD images.
LIVECDS := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -live-iso,$(SYSTEM)))

# These are targets supported by the kickstart/Makefile that will be used to generate installation ISOs.
INSTISOS := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -inst-iso,$(SYSTEM)))

# These are targets supported by the kickstart/Makefile that will be used to generate AWS AMI 
AWSBUNDLES := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -aws-ami,$(SYSTEM)))

# Add a file to a repo by either downloading it (if http/ftp), or symlinking if local.
# TODO: add support for wget (problem with code below, running echo/GREP for each file instead of once for the whole repo
#@if ( echo "$(2)" | $(GREP) -i -q '^http[s]?://|^ftp://' ); then\
#	$(REPO_WGET) $(2)/$(1) -O $(3)/$(1);\
#else\
#	$(REPO_LINK) $(2)/$(1) $(3)/$(1);\
#fi
define REPO_ADD_FILE
	$(VERBOSE)[ -h $(3)/$(1) ] || $(REPO_LINK) $(2)/$(1) $(3)/$(1)
endef

define CHECK_DEPS
	@if ! rpm -q $(HOST_RPM_DEPS) 2>&1 >/dev/null; then echo "Please ensure the following RPMs are installed: $(HOST_RPM_DEPS)."; exit 1; fi
	@if [ x"`cat /selinux/enforce`" == "x1" ]; then echo -e "This is embarassing but due to a bug (bz #861281) you must do builds in permissive.\nhttps://bugzilla.redhat.com/show_bug.cgi?id=861281" && exit 1; fi
endef

define CHECK_MOCK
	@if ps -eo comm= | grep -q mock; then echo "ERROR: Another instance of mock is running.  Please hangup and try your build again later." && exit 1; fi
endef

AVAIL_ZONES := us-east-1 us-west-1 us-west-2 eu-west-1 eu-central-1 ap-southeast-1 ap-southeast-2 ap-northeast-1 sa-east-1
FILTERED_ZONE := $(filter $(AVAIL_ZONES), $(AWS_AVAIL_ZONE))

define CHECK_AWS_VARS
	@if [ x"$(AWS_SIGNING_CERT)" == "x" ]; then echo -e "In CONFIG_AWS, set AWS_SIGNING_CERT to the path to your AWS signing certificate"; exit -1; fi
	@if [ x"$(AWS_PRIV_KEY)" == "x" ]; then echo -e "In CONFIG_AWS, set AWS_PRIV_KEY to the path to your AWS private key"; exit -1; fi
	@if [ x"$(AWS_ACCT_ID)" == "x" ]; then echo -e "In CONFIG_AWS, set AWS_ACCT_ID to your AWS account ID"; exit -1; fi
	@if [ x"$(AWS_ACCESS_KEY_ID)" == "x" ]; then echo -e "In CONFIG_AWS, set AWS_ACCESS_KEY_ID to your AWS access key ID"; exit -1; fi
	@if [ x"$(AWS_ACCESS_KEY)" == "x" ]; then echo -e "In CONFIG_AWS, set AWS_ACCESS_KEY to your AWS access key"; exit -1; fi
	@if [ x"$(AWS_AVAIL_ZONE)" == "x" ]; then echo -e "In CONFIG_AWS, set AWS_AVAIL_ZONE to your desired AWS availability zone"; exit -1; fi
	@if [ x"$(FILTERED_ZONE)" == "x" ]; then echo -e "AWS_AVAIL_ZONE is invalid, should be one of \"$(AVAIL_ZONES)\"" ; exit -1; fi
	@echo "AWS variables are all set."
endef

define MAKE_LIVE_TOOLS
	$(MAKE) livecd-tools-rpm; \
	mkdir -p $(TOOLS_DIR); \
	cp $(CLIP_REPO_DIR)/livecd-tools-$(LIVECD_VERSION).noarch.rpm $(TOOLS_DIR); \
	cp $(CLIP_REPO_DIR)/python-imgcreate-$(LIVECD_VERSION).noarch.rpm $(TOOLS_DIR); \
	rpm2cpio $(TOOLS_DIR)/livecd-tools-$(LIVECD_VERSION).noarch.rpm > $(TOOLS_DIR)/livecd-tools-$(LIVECD_VERSION).noarch.rpm.cpio; \
	rpm2cpio $(TOOLS_DIR)/python-imgcreate-$(LIVECD_VERSION).noarch.rpm > $(TOOLS_DIR)/python-imgcreate-$(LIVECD_VERSION).noarch.rpm.cpio; \
	cd $(TOOLS_DIR) && cpio -idv < livecd-tools-$(LIVECD_VERSION).noarch.rpm.cpio && \
	cpio -idv < python-imgcreate-$(LIVECD_VERSION).noarch.rpm.cpio;
endef

define MAKE_PUNGI
	$(MAKE) pungi-rpm; \
	mkdir -p $(TOOLS_DIR); \
	cp $(CLIP_REPO_DIR)/pungi-$(PUNGI_VERSION).noarch.rpm $(TOOLS_DIR); \
	rpm2cpio $(TOOLS_DIR)/pungi-$(PUNGI_VERSION).noarch.rpm > $(TOOLS_DIR)/pungi-$(PUNGI_VERSION).noarch.rpm.cpio; \
	cd $(TOOLS_DIR) && cpio -idv < pungi-$(PUNGI_VERSION).noarch.rpm.cpio
endef

######################################################
# BEGIN RPM GENERATION RULES (BEWARE OF DRAGONS)
# This define directive is used to generate build rules.
define RPM_RULE_template
$(1): $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1))) $(MY_REPO_DEPS) $(MOCK_CONF_DIR)/$(MOCK_REL).cfg $(YUM_CONF_ALL_FILE) $(CLIP_REPO_DIR)/exists
	$(call CHECK_DEPS)
	$(call MKDIR,$(CLIP_REPO_DIR))
	$(call CHECK_MOCK)
	$(VERBOSE)$(MOCK) $(MOCK_ARGS) $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1)))
	cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(COMPS_FILE)  .
	$(VERBOSE)$(call REPO_QUERY,$(YUM_CONF_ALL_FILE)) --repoid=clip-repo |sort 1>$(CONF_DIR)/pkglist.clip-repo
ifeq ($(ENABLE_SIGNING),y)
	$(RPM) --addsign $(CLIP_REPO_DIR)/*
endif

$(eval PHONIES += $(call PKG_NAME_FROM_RPM,$(notdir $(1)))-rpm $(call PKG_NAME_FROM_RPM,$(notdir $(1)))-nomock-rpm)
$(call PKG_NAME_FROM_RPM,$(notdir $(1)))-rpm:  $(1)
$(call PKG_NAME_FROM_RPM,$(notdir $(1)))-nomock-rpm:  $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1)))
	$(call CHECK_DEPS)
	$(call MKDIR,$(CLIP_REPO_DIR))
	$(VERBOSE)OUTPUT_DIR=$(CLIP_REPO_DIR) $(MAKE) -C $(PKG_DIR)/$(call PKG_NAME_FROM_RPM,$(notdir $(1))) rpm
	cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(COMPS_FILE) .

$(eval PHONIES += $(call PKG_NAME_FROM_RPM,$(notdir $(1)))-srpm $(call PKG_NAME_FROM_RPM,$(notdir $(1)))-clean)
$(call PKG_NAME_FROM_RPM,$(notdir $(1)))-srpm:  $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1)))
$(call PKG_NAME_FROM_RPM,$(notdir $(1)))-clean:
	$(call CHECK_DEPS)
	$(RM) $(1)
	$(RM) $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1)))
endef
# END RPM GENERATION RULES (BEWARE OF DRAGONS)
######################################################

GET_REPO_ID = $(strip $(shell echo "$(1)" | $(SED) -e 's/\(.*\)=.*/\1/'))
GET_REPO_PATH = $(strip $(shell echo "$(1)" | $(SED) -e 's/.*=\(.*\)/\1/'))
GET_REPO_URL = $(strip $(shell if `echo "$(1)" | $(GREP) -Eq '^\/.*$$'`; then echo "file://$(1)"; else echo "$(1)"; fi))

######################################################
# BEGIN REPO GENERATION RULES (BEWARE OF RMS)
# This define directive is used to generate rules for managing the yum repos.
# Since the user of the build system can customize the repos in CONFIG_REPOS
# we need to generate targets out of the contents of that file.  The previous
# implementation had static rules and required a lot of work to add/remove
# or otherwise customize the repos.
define REPO_RULE_template
$(eval REPO_ID := $(call GET_REPO_ID, $(1)))
ifneq ($(strip $(1)),)
$(eval REPO_PATH := $(call GET_REPO_PATH,$(1)))
$(eval REPO_URL := $(call GET_REPO_URL,$(call GET_REPO_PATH,$(1))))
$(eval setup_all_repos += setup-$(REPO_ID)-repo)

$(eval YUM_CONF := [$(REPO_ID)]\\nname=$(REPO_ID)\\nbaseurl=$(REPO_URL)\\nenabled=1\\n\\nexclude=$(strip $(PKG_BLACKLIST))\\n)
$(eval MOCK_YUM_CONF := $(MOCK_YUM_CONF)[$(REPO_ID)]\\nname=$(REPO_ID)\\nbaseurl=file://$(REPO_DIR)/$(REPO_ID)-repo\\nenabled=1\\n\\nexclude=$(strip $(PKG_BLACKLIST))\\n)
$(eval MY_REPO_DEPS += $(REPO_DIR)/$(REPO_ID)-repo/last-updated)
$(eval REPO_LINES := $(REPO_LINES)repo --name=$(REPO_ID) --baseurl=file://$(REPO_DIR)/$(REPO_ID)-repo\n)

$(eval CLIP_REPO_DIRS += "$(REPO_DIR)/$(REPO_ID)-repo")
$(eval PKG_LISTS += "./$(shell basename $(CONF_DIR))/pkglist.$(REPO_ID)")
$(eval REPO_DEPS += $(REPO_DIR)/$(REPO_ID)-repo/last-updated)

$(eval PHONIES += setup-$(REPO_ID)-repo)
setup-$(REPO_ID)-repo:  $(REPO_DIR)/$(REPO_ID)-repo/last-updated $(CONFIG_BUILD_DEPS) 

# This is the key target for managing yum repos.  If the pkg list for the repo
# is more recent then our private repo regen the repo by symlink'ing the packages into our repo.
$(REPO_DIR)/$(REPO_ID)-repo/last-updated: $(CONF_DIR)/pkglist.$(REPO_ID) $(CONFIG_BUILD_DEPS)
	@echo "Cleaning $(REPO_ID) yum repo, this could take a few minutes..."
	$(VERBOSE)$(RM) -r $(REPO_DIR)/$(REPO_ID)-repo
	@echo "Populating $(REPO_ID) yum repo, this could take a few minutes..."
	@if [ ! -d $(REPO_PATH) ]; then echo -e "\nError yum repo path doesn't exist: $(REPO_PATH)\n"; exit 1; fi
	$(call MKDIR,$(REPO_DIR)/$(REPO_ID)-repo)
	$(VERBOSE)while read fil; do $(REPO_LINK) $(REPO_PATH)/$$$$fil $(REPO_DIR)/$(REPO_ID)-repo/$$$$fil; done < $(CONF_DIR)/pkglist.$(REPO_ID)
	@echo "Generating $(REPO_ID) yum repo metadata, this could take a few minutes..."
	$(VERBOSE)cd $(REPO_DIR)/$(REPO_ID)-repo && $(REPO_CREATE) -g $(COMPS_FILE)  .
	test -f $(YUM_CONF_ALL_FILE) || ( cat $(YUM_CONF_FILE).tmpl > $(YUM_CONF_ALL_FILE);\
		echo -e "[clip-repo]\\nname=clip-repo\\nbaseurl=file://$(CLIP_REPO_DIR)/\\nenabled=1\\n" >> $(YUM_CONF_ALL_FILE)) 
	echo -e $(YUM_CONF) >> $(YUM_CONF_ALL_FILE)
	$(VERBOSE)touch $(REPO_DIR)/$(REPO_ID)-repo/last-updated

# If a pkglist is missing then assume we should generate one ourselves.
# Note that the recommended method here is to commit your pkglist file to your own dev repo.
# Then you can consistently rebuild an ISO using the exact same package versions as the last time.
# Effectively versioning the packages you use when rolling RPMs and ISOs.
$(CONF_DIR)/pkglist.$(REPO_ID) ./$(shell basename $(CONF_DIR))/pkglist.$(REPO_ID): $(filter-out $(ROOT_DIR)/CONFIG_BUILD,$(CONFIG_BUILD_DEPS)) $(CONF_DIR)/pkglist.blacklist $(REPO_PATH)/repodata/repomd.xml
	$(VERBOSE)rm -rf $(REPO_DIR)/$(REPO_ID)-repo
	$(VERBOSE)$(RM) $(YUM_CONF_FILE)
	$(VERBOSE)$(RM) $(MOCK_CONF_DIR)/$(MOCK_REL).cfg
	@echo "Generating list of packages for $(call GET_REPO_ID,$(1))"
	$(VERBOSE)cat $(YUM_CONF_FILE).tmpl > $(YUM_CONF_FILE)
	echo -e $(YUM_CONF) >> $(YUM_CONF_FILE)
	$(VERBOSE)$(call REPO_QUERY,$(YUM_CONF_FILE)) --repoid=$(REPO_ID) |sort 1>$(CONF_DIR)/pkglist.$(REPO_ID)

endif
endef
# END REPO GENERATION RULES (BEWARE OF RMS)
######################################################

######################################################
# BEGIN RULES

PHONIES += help
help:
	$(call CHECK_DEPS)
	@echo "The following make targets are available for generating installable ISOs:"
	@echo "	all"
	@for cd in $(INSTISOS); do echo "	$$cd"; done
	@echo
	@echo "The following make targets are available for generating Live CDs:"
	@echo "	all"
	@for cd in $(LIVECDS); do echo "	$$cd"; done
	@echo
	@echo "The following make targets are available for generating AWS :"
	@for cd in $(AWSBUNDLES); do echo "	$$cd"; done
	@echo
	@echo "To burn a livecd image to a thumbdrive:"
	@echo "	iso-to-disk ISO_FILE=<isofilename> USB_DEV=<devname>"
	@echo "	iso-to-disk ISO_FILE=<isofilename> USB_DEV=<devname> OVERLAY_SIZE=<size in MB>"
	@echo "	iso-to-disk ISO_FILE=<isofilename> USB_DEV=<devname> OVERLAY_SIZE=<size in MB> OVERLAY_HOME_SIZE=<size in MB>"
	@echo
	@echo "The following make targets are available for generating RPMs in mock:"
	@echo "	rpms (generate all rpms in mock)"
	@for pkg in $(PACKAGES); do echo "	$$pkg-rpm"; done
	@echo
	@echo "The following make targets are available for generating RPMs without mock:"
	@for pkg in $(PACKAGES); do echo "	$$pkg-nomock-rpm"; done
	@echo
	@echo "The following make targets are available for generating SRPMS:"
	@echo "	srpms (generate all src rpms)"
	@for pkg in $(PACKAGES); do echo "	$$pkg-srpm"; done
	@echo
	@echo "The following make targets are available for updating the package lists used for mock and ISO generation:"
	@for pkg in $(PKG_LISTS); do echo "	$$pkg"; done
	@echo
	@echo "The following make targets are available for generating yum repos used for mock and ISO generation:"
	@for repo in $(setup_all_repos); do echo "	$$repo"; done
	@echo
	@echo "The following make targets are available for cleaning:"
	@for pkg in $(PACKAGES); do echo "	$$pkg-clean (remove rpm and srpm)"; done
	@echo "	clean (cleans transient files)"
	@echo "	bare-repos (deletes local repos)"
	@echo "	clean-mock (deletes the yum and mock configuration we generate)"
	@echo "	bare (deletes everything except ISOs)"

PHONIES += all
all: $(INSTISOS) $(LIVECDS)

# Generate custom targets for managing the yum repos.  We have to generate the rules since the user provides the set of repos.
$(foreach REPO,$(strip $(shell cat CONFIG_REPOS|$(GREP) -E '^[a-zA-Z].*=.*'|$(SED) -e 's/ \?= \?/=/')),$(eval $(call REPO_RULE_template,$(REPO))))

# The following line calls our RPM rule template defined above allowing us to build a proper dependency list.
$(foreach RPM,$(RPMS),$(eval $(call RPM_RULE_template,$(RPM))))

# We need some packages on the build host that aren't available in EPEL, RHEL, Opt.
SRPMS := $(SRPMS) $(addprefix $(SRPM_OUTPUT_DIR)/,$(foreach RPM,$(HOST_RPMS),$(call SRPM_FROM_RPM,$(notdir $(RPM)))))

# This is a slight hack to make sure we have a valid yum repo here.
# Problem is, the repodata files are re-generated every time an PRM is built.
# This means depending on something like repo.md causes every package to be 
# built every single time.  So we'll use this to fake it.
$(CLIP_REPO_DIR)/exists:  
	$(call CHECK_DEPS)
	$(call MKDIR,$@)
	echo "Generating clip-repo metadata."; \
	$(VERBOSE)cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(COMPS_FILE) .

	@set -e; for pkg in $(PRE_ROLLED_PACKAGES); do \
           [ -f "$$pkg" ] || ( echo "Failed to find pre-rolled package: $$pkg" && exit 1 );\
           [ -h $(CLIP_REPO_DIR)/`basename $$pkg` ] && rm -f $(CLIP_REPO_DIR)/`basename $$pkg`;\
              $(REPO_LINK) $$pkg $(CLIP_REPO_DIR)|| \
	      ( echo "Failed to find pre-rolled package $$pkg - check CONFIG_BUILD and make sure you use quotes around paths with spaces." && exit 1 );\
        done
	$(VERBOSE)cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(COMPS_FILE) .
	touch $@

PHONIES += rpms
rpms: $(RPMS)

PHONIES += srpms
srpms: $(SRPMS)

%.src.rpm:  FORCE
	$(call CHECK_DEPS)
	$(call MKDIR,$(SRPM_OUTPUT_DIR))
	$(MAKE) -C $(PKG_DIR)/$(call PKG_NAME_FROM_RPM,$(notdir $@)) srpm

PHONIES += $(LIVECDS)
$(LIVECDS):  $(CONFIG_BUILD_DEPS) $(RPMS)
	$(call CHECK_DEPS)
	$(call MAKE_LIVE_TOOLS)
	$(MAKE) -f $(KICKSTART_DIR)/Makefile -C $(KICKSTART_DIR)/"`echo '$(@)'|$(SED) -e 's/\(.*\)-live-iso/\1/'`" live-iso

PHONIES += $(INSTISOS)
$(INSTISOS):  $(CONFIG_BUILD_DEPS) $(RPMS)
	$(call CHECK_DEPS)
	$(call MAKE_PUNGI)
	$(MAKE) -f $(KICKSTART_DIR)/Makefile -C $(KICKSTART_DIR)/"`echo '$(@)'|$(SED) -e 's/\(.*\)-inst-iso/\1/'`" iso

$(EC2_AMI_TOOLS_ZIP):
	@test -d $(RPM_TMPDIR) || mkdir -p $(RPM_TMPDIR)
	curl -o $@ $(EC2_AMI_TOOLS_URL)

$(EC2_AMI_TOOLS): $(EC2_AMI_TOOLS_ZIP)
	unzip -d $@ $^

$(EC2_API_TOOLS_ZIP):
	@test -d $(RPM_TMPDIR) || mkdir -p $(RPM_TMPDIR)
	curl -o $@ $(EC2_API_TOOLS_URL)

$(EC2_API_TOOLS): $(EC2_API_TOOLS_ZIP)
	unzip -d $@ $^

PHONIES += ec2-tools
ec2-tools: $(EC2_AMI_TOOLS) $(EC2_API_TOOLS)

PHONIES += check-vars
check-vars:
	$(call CHECK_AWS_VARS)


$(AWSBUNDLES): check-vars ec2-tools $(CONFIG_BUILD_DEPS) $(RPMS)
	$(call CHECK_DEPS)
	$(call MAKE_LIVE_TOOLS)
	# TODO: this awk expression relies heavily on the tool name prefix length, better option?
	$(MAKE) -f $(KICKSTART_DIR)/Makefile -C $(KICKSTART_DIR)/"`echo '$(@)'|$(SED) -e 's/\(.*\)-aws-ami/\1/'`" \
		EC2_API_TOOLS_VER=$$(unzip -l $(EC2_API_TOOLS_ZIP)|awk '/^.*[0-9]\/$$/ { print substr($$4,15,length($$4)-15); }') aws 

$(MOCK_CONF_DIR)/$(MOCK_REL).cfg:  $(MOCK_CONF_DIR)/$(MOCK_REL).cfg.tmpl $(CONF_DIR)/pkglist.blacklist $(CLIP_REPO_DIR)/exists
	$(call CHECK_DEPS)
	$(VERBOSE)cat $(MOCK_CONF_DIR)/$(MOCK_REL).cfg.tmpl > $@
	$(VERBOSE)echo -e $(MOCK_YUM_CONF) >> $@
	$(VERBOSE)echo -e "[clip-repo]\\nname=clip-repo\\nbaseurl=file://$(CLIP_REPO_DIR)/\\nenabled=1\\n" >> $@
	$(VERBOSE)echo '"""' >> $@

ifneq ($(OVERLAY_HOME_SIZE),)
OVERLAYS += --home-size-mb $(OVERLAY_HOME_SIZE)
endif
ifneq ($(OVERLAY_SIZE),)
OVERLAYS += --overlay-size-mb $(OVERLAY_SIZE)
endif

PHONIES += iso-to-disk
iso-to-disk:
	@if [ x"$(ISO_FILE)" = "x" -o x"$(USB_DEV)" = "x" ]; then echo "Error: set ISO_FILE=<filename> and USB_DEV=<dev> on command line to generate a bootable thumbdrive." && exit 1; fi
	@if echo "$(USB_DEV)" | $(GREP) -q "^.*[0-9]$$"; then echo "Error: it looks like you gave me a partition.  Set USB_DEV to a device root, eg /dev/sdb." && exit 1; fi
	@if [ ! -b $(USB_DEV) ]; then echo "Error: $(USB_DEV) doesn't exist or isn't a block device." && exit 1; fi
	@if `sudo mount | $(GREP) -q $(USB_DEV)`; then echo "Warning - device is currently mounted!  I will unmount it for you.  Press Ctrl-C to cancel or any other key to continue."; read; sudo umount $(USB_DEV)1 2>&1 > /dev/null; fi
	@if `sudo pvdisplay 2>/dev/null | $(GREP) -q $(USB_DEV)`; then echo "Warning - device is currently a a physical volume in an LVM configuration!  This usually means you're pointing me at your root filesystem instead of a thumbdrive. Try again or kill the LVM label with pvremove"; exit 1; fi
	@echo -e "WARNING: This will destroy the contents of $(USB_DEV)!\nPress Ctrl-C to cancel or any other key to continue." && read
	@echo "Destroying MBR and partition table."
	$(VERBOSE)sudo dd if=/dev/zero of=$(USB_DEV) bs=512 count=1
	@echo "Creating partition..."
	$(VERBOSE)sudo sh -c "echo -e 'n\np\n1\n\n\n\nt\nb\na\n1\nw\n' | /sbin/fdisk $(USB_DEV)" || true
	@sleep 5
	$(VERBOSE)sudo umount $(USB_DEV)1 2>&1 > /dev/null || true
	@echo "Creating filesystem..."
	$(VERBOSE)sudo /sbin/mkdosfs -n CLIP $(USB_DEV)1
	$(VERBOSE)sudo umount $(USB_DEV)1 2>&1 > /dev/null || true
	@echo "Writing image..."
	$(VERBOSE)sudo /usr/bin/livecd-iso-to-disk $(OVERLAYS) --resetmbr $(ISO_FILE) $(USB_DEV)1

PHONIES += clean-mock
clean-mock: $(ROOT_DIR)/CONFIG_REPOS $(ROOT_DIR)/Makefile $(CONF_DIR)/pkglist.blacklist
	$(VERBOSE)$(RM) $(YUM_CONF_FILE)
	$(VERBOSE)$(RM) $(MOCK_CONF_DIR)/$(MOCK_REL).cfg
	$(VERBOSE)$(RM) -rf $(REPO_DIR)/yumcache

PHONIES += bare-repos
bare-repos: clean-mock
	$(VERBOSE)$(RM) $(YUM_CONF_ALL_FILE)
	$(VERBOSE)$(RM) -rf repos/*

PHONIES += clean
clean:
	@sudo $(RM) -rf $(RPM_TMPDIR) $(TOOLS_DIR)
	@$(VERBOSE)for pkg in $(PACKAGES); do $(MAKE) -C $(PKG_DIR)/$$pkg $@; done

PHONIES += bare
bare: bare-repos clean
	for pkg in $(PACKAGES); do $(MAKE) -C $(PKG_DIR)/$$pkg $@; done
	$(VERBOSE)$(RM) $(addprefix $(SRPM_OUTPUT_DIR),$(SRPMS))
	$(VERBOSE)$(RM) $(addprefix $(OUTPUT_DIR),$(RPMS))

PHONIES += FORCE
FORCE:

# Unfortunately mock isn't exactly "parallel" friendly which sucks since we could roll a bunch of packages in parallel.
.NOTPARALLEL:
.SUFFIXES:
.PHONY: $(PHONIES) $(YUM_CONF_PHONIES) 


# END RULES
######################################################
