# Copyright (C) 2011-2012 Tresys Technology, LLC
# Copyright (C) 2011-2016 Quark Security, Inc
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
export RHEL_VER := 8
export CENTOS_VER := 8

######################################################
# BEGIN MAGIC
ifneq ($(QUIET),y)
$(info Boot strapping build system...)
endif

# This lets sub-makes take actions based on the full OS rver+release found in the mock repos instead of on host version
# E.g., the SELinux policy uses different spec files based on release
# Make sure $(YUM_CONF_ALL_FILE) is a dep for any recipes that use this feature
define OS_REL
$(strip $(shell test -f $(YUM_CONF_ALL_FILE) && repoquery -c $(YUM_CONF_ALL_FILE) --provides $$(repoquery -c $(YUM_CONF_ALL_FILE) --whatprovides "system-release") | awk ' /^system-release =/ { gsub(/-.*/,"",$$3); print $$3}'))
endef

# NOTE: DO NOT REMOVE THIS CHECK. RUNNING MOCK AS ROOT *WILL* BREAK THINGS.
ifeq ($(shell id -u),0)
$(error Never build CLIP as root! The tools used by CLIP (mock) will break things! Try again as an unprivileged user with sudo access.)
endif

HOST_RPM_DEPS := $(shell ./support/get-host-deps.sh all)

export ROOT_DIR ?= $(CURDIR)
export OUTPUT_DIR ?= $(ROOT_DIR)
export RPM_TMPDIR ?= $(ROOT_DIR)/tmp
export YUM_CACHEDIR ?= $(ROOT_DIR)/tmp/yumcache
export CONF_DIR ?= $(ROOT_DIR)/conf
export TOOLS_DIR ?= $(ROOT_DIR)/tmp/tools

LIVECD_RPMS = $(shell ./support/get-rpms-from-spec.sh packages/livecd-tools/livecd-tools.spec)
PUNGI_RPMS = $(shell ./support/get-rpms-from-spec.sh packages/pungi/pungi.spec)
LORAX_RPMS = $(shell ./support/get-rpms-from-spec.sh packages/lorax/lorax.spec)

# Config deps
CONFIG_BUILD_DEPS := $(ROOT_DIR)/CONFIG_BUILD $(ROOT_DIR)/CONFIG_REPOS $(ROOT_DIR)/Makefile $(CONF_DIR)/pkglist.blacklist

# MOCK_REL must be configured in MOCK_CONF_DIR/MOCK_REL.cfg
MOCK_REL := rhel-$(RHEL_VER)-$(TARGET_ARCH)

# This directory contains all of our packages we will be building.
PKG_DIR += $(CURDIR)/packages

#determine which variants we're building
VARIANTS := $(filter %-inst-iso %-inst-iso-fast %-live-iso %-aws-ami,$(MAKECMDGOALS))
VARIANTS := $(subst -inst-iso-fast,,$(VARIANTS))
VARIANTS := $(subst -inst-iso,,$(VARIANTS))
VARIANTS := $(subst -aws-ami,,$(VARIANTS))
VARIANTS := $(subst -live-iso,,$(VARIANTS))
ifeq ($(strip $(VARIANTS)),)
PACKAGES := $(shell ls $(PKG_DIR) | grep -v examples|grep -v strongswan)
else
$(foreach VARIANT,$(VARIANTS), $(eval include kickstart/$(VARIANT)/variant_pkgs.mk))
endif

ifneq ($(CONFIG_BUILD_ENABLE_GUI),n)
PACKAGES += clip-gnome-extensions
endif



# FIXME: remove when AWS is supported by CLIP for v7
ifneq ($(filter %-aws-ami,$(MAKECMDGOALS)),)
$(error "AWS/EC2 targets not supported for RHEL/CentOS v7 quite yet. Stay tuned.")
endif
#
# FIXME: remove when VPN variants supported by CLIP for v7
ifneq ($(filter wip-clip-vpn-%,$(MAKECMDGOALS)),)
$(warning The CLIP VPN variant is not functional for RHEL v7 quite yet due to a switch to libreswan from strongswan. You've been warned.)
$(shell sleep 5)
endif
# FIXME: remove when Kubes variants supported by CLIP for v7
ifneq ($(filter wip-clip-kubernetes-%,$(MAKECMDGOALS)),)
$(warning The CLIP Kubernetes variant has not been well-tested quite yet. You've been warned.)
$(shell sleep 5)
endif

# if trying to build a fast ISO, check for DONOR_ISO before we waste time trying to build everything
ifneq ($(filter %-inst-iso-fast,$(MAKECMDGOALS)),)
ifeq ($(DONOR_ISO),)
$(info           )
$(info I've detected a problem with your fast ISO configuration.)
$(info When building *-inst-iso-fast targets DONOR_ISO must be set on the command line and be a path to a valid RHEL/CLIP ISO to use as a starting point.)
$(error No DONOR_ISO specification)
endif
ifeq ($(wildcard $(DONOR_ISO) $(CURDIR)/$(DONOR_ISO)),)
$(info           )
$(info I've detected a problem with your fast-iso configuration.)
$(info If you are building *-inst-iso-fast targets, DONOR_ISO must point to a valid RHEL/CLIP ISO.)
$(info The ISO will be used as a starting point when building the new image.)
$(info           )
$(info DONOR_ISO is currently set to:)
$(info $(shell echo -e "\tDONOR_ISO =" $(DONOR_ISO)))
$(info Because I love you, I also tried:)
$(info $(shell echo -e "\tDONOR_ISO =" $(CURDIR)/$(DONOR_ISO) in case you gave me a relative path.))
$(error Bad DONOR_ISO specification)
else ifneq ($(wildcard $(CURDIR)/$(DONOR_ISO)),)
$(info           )
$(info Looks like the DONOR_ISO is a relative path.)
$(info Assuming current directory. If this is not your intention, ctrl-c and update the DONOR_ISO variable on the command-line.)
$(shell sleep 3)
override DONOR_ISO := $(CURDIR)/$(DONOR_ISO)
endif
endif

ifneq ($(DONOR_ISO),)
ifneq ($(filter %-inst-iso-fast,$(MAKECMDGOALS)),)
$(info           )
$(info Building a fast ISO using this as a starting point:)
$(info $(shell echo -e "\tDONOR_ISO =" $(DONOR_ISO)))
$(info This will save *a lot* of time, but the ISO should not be used in production as the full contents of the image will not be captured in the CLIP repo.)
$(info           )
$(shell sleep 3)
endif
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
export CLIP_REPO_DIRS :=

# These are the directories where we will put our custom copies of
# the yum repos.  These will be removed by "make bare".
export CLIP_REPO_DIR := $(REPO_DIR)/clip-repo
CLIP_SRPM_REPO_DIR := $(REPO_DIR)/clip-srpms
export REPO_LINES := repo --name=clip-repo --baseurl=file://$(CLIP_REPO_DIR)\n

export SRPM_OUTPUT_DIR := $(CLIP_SRPM_REPO_DIR)

export MAYFLOWER := $(SUPPORT_DIR)/mayflower

SED := /bin/sed
GREP := /bin/egrep
MOCK := /usr/bin/mock
REPO_LINK := /bin/ln -s
REPO_WGET := /usr/bin/wget
REPO_CREATE := /usr/bin/createrepo -d --workers $(shell /usr/bin/nproc) --simple-md-filenames -c $(REPO_DIR)/yumcache
FIND_COMPS = $(shell found_comps=$$(find "$(1)" -type f -name '*comps-*.xml'); test -z "$$found_comps" && echo $(COMPS_FILE) || echo $$found_comps)
FIND_MODMD = $(shell find "$(1)" -type f -name '*modules.yaml.gz')
REPO_QUERY = repoquery -c $(1) --quiet -a --queryformat '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm'
MOCK_ARGS += --resultdir=$(CLIP_REPO_DIR) -r $(MOCK_REL) --configdir=$(MOCK_CONF_DIR) --unpriv --rebuild --uniqueext=$(shell echo $$USER)

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

# Multiple kickstart/foo/variants_pkgs.mk can include the same pacakge name, remove dupes
# to avoid redeclaring recipes for the same target
PACKAGES := $(sort $(PACKAGES))

# Create the list of RPMs based on package list.
RPMS := $(addprefix $(CLIP_REPO_DIR)/,$(foreach PKG,$(PACKAGES),$(call RPM_FROM_PKG_NAME,$(strip $(PKG)))))
SRPMS := $(addprefix $(SRPM_OUTPUT_DIR)/,$(foreach RPM,$(RPMS),$(call SRPM_FROM_RPM,$(notdir $(RPM)))))

ifeq ($(QUIET),y)
	VERBOSE = @
endif

MKDIR = $(VERBOSE)test -d $(1) || mkdir -p $(1)

SYSTEMS := $(shell find $(KICKSTART_DIR) -maxdepth 1 ! -name kickstart ! -name includes -type d -printf "%f\n")

# These are targets supported by the kickstart/Makefile that will be used to generate LiveCD images.
LIVECDS := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -live-iso,$(SYSTEM)))

# Targets for fast gen'd dev ISOs
FASTINSTISOS := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -inst-iso-fast,$(SYSTEM)))

# These are targets supported by the kickstart/Makefile that will be used to generate installation ISOs.
INSTISOS := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -inst-iso,$(SYSTEM)))

# Targets for gen'ing images suitable for uploading to AWS
AWSBUNDLES := $(foreach SYSTEM,$(SYSTEMS),$(addsuffix -aws-ami,$(SYSTEM)))

# macro used to gather interdependencies between packages built from source
PKG_DEPS = $(strip $(eval $(shell $(GREP) ^DEPS $(PKG_DIR)/$(1)/Makefile || echo "DEPS :="))$(DEPS))

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
	@if [ x"`cat /sys/fs/selinux/enforce`" == "x1" ]; then echo -e "This is embarassing but due to a bug (bz #861281) you must do builds in permissive.\nhttps://bugzilla.redhat.com/show_bug.cgi?id=861281" && exit 1; fi
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

define INSTALL_TOOLS
	mkdir -p $(TOOLS_DIR) && \
	for p in $(1); do \
	    rpm2cpio $(CLIP_REPO_DIR)/$$p | \
	        cpio -D $(TOOLS_DIR) -idv; \
	done
endef

define MAKE_LIVE_TOOLS
	$(MAKE) livecd-tools-rpm && \
	$(call INSTALL_TOOLS,$(LIVECD_RPMS))
endef

define MAKE_PUNGI
	$(MAKE) pungi-rpm && \
	$(call INSTALL_TOOLS,$(PUNGI_RPMS))
endef

define MAKE_LORAX
	$(MAKE) lorax-rpm && \
	$(call INSTALL_TOOLS,$(LORAX_RPMS))
endef

######################################################
# BEGIN RPM GENERATION RULES (BEWARE OF DRAGONS)
# This define directive is used to generate build rules.
define RPM_RULE_template
$(1): $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1))) $(MY_REPO_DEPS) $(MOCK_CONF_DIR)/$(MOCK_REL).cfg $(YUM_CONF_ALL_FILE) $(CLIP_REPO_DIR)/exists
$(1): $(addprefix $(CLIP_REPO_DIR)/,$(foreach DEP,$(call PKG_DEPS,$(call PKG_NAME_FROM_RPM,$(notdir $(1)))),$(call RPM_FROM_PKG_NAME,$(DEP))))
	$(call CHECK_DEPS)
	$(call MKDIR,$(CLIP_REPO_DIR))
	$(VERBOSE)$(MOCK) $(MOCK_ARGS) $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1)))
	cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(call FIND_COMPS,$(REPO_PATH)) .
	$(VERBOSE)$(call REPO_QUERY,$(YUM_CONF_ALL_FILE)) --repoid=clip-repo 2>/dev/null|sort 1>$(CONF_DIR)/pkglist.clip-repo
ifeq ($(ENABLE_SIGNING),y)
	$(RPM) --addsign $(CLIP_REPO_DIR)/*
endif

$(eval PHONIES += $(call PKG_NAME_FROM_RPM,$(notdir $(1)))-rpm $(call PKG_NAME_FROM_RPM,$(notdir $(1)))-nomock-rpm)
$(call PKG_NAME_FROM_RPM,$(notdir $(1)))-rpm:  $(1)
# TODO: we do not yet handle deps for nomock as we put the same output RPMs in the same location of mock'd RPMs.
# In essence, we do not know if the RPM that exists was built inside or outside of mock
# so for now, clobber the output RPM and rebuild
$(call PKG_NAME_FROM_RPM,$(notdir $(1)))-nomock-rpm:
	$(call CHECK_DEPS)
	$(call MKDIR,$(CLIP_REPO_DIR))
	$(RM) $(SRPM_OUTPUT_DIR)/$(call SRPM_FROM_RPM,$(notdir $(1)))
	$(VERBOSE)OUTPUT_DIR=$(CLIP_REPO_DIR) $(MAKE) -C $(PKG_DIR)/$(call PKG_NAME_FROM_RPM,$(notdir $(1))) srpm rpm
	cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(call FIND_COMPS,$(REPO_PATH)) .

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
$(eval REPO_FAILED += $(strip $(shell [ -n "$$(/usr/bin/find $(REPO_PATH) -type f -name repomd.xml 2>/dev/null)" ] || echo $(REPO_PATH))))
$(eval setup_all_repos += setup-$(REPO_ID)-repo)
$(eval YUM_CONF := [$(REPO_ID)]\\nname=$(REPO_ID)\\nbaseurl=$(REPO_URL)\\nenabled=1\\n\\nexclude=$(strip $(PKG_BLACKLIST))\\n)
$(eval MOCK_YUM_CONF := $(MOCK_YUM_CONF)[$(REPO_ID)]\\nname=$(REPO_ID)\\nbaseurl=file://$(REPO_DIR)/$(REPO_ID)-repo\\nenabled=1\\n\\nexclude=$(strip $(PKG_BLACKLIST))\\n)
$(eval MY_REPO_DEPS += $(REPO_DIR)/$(REPO_ID)-repo/last-updated)
$(eval REPO_LINES := $(REPO_LINES)repo --name=$(REPO_ID) --baseurl=file://$(REPO_DIR)/$(REPO_ID)-repo\n)

$(eval export CLIP_REPO_DIRS += "$(REPO_DIR)/$(REPO_ID)-repo")
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
# TODO: This mess needs to be addressed using repoquery's relativepath tag.
	@if [ ! -d $(REPO_PATH) ]; then echo -e "\nError yum repo path doesn't exist: $(REPO_PATH)\n"; exit 1; fi
	$(call MKDIR,$(REPO_DIR)/$(REPO_ID)-repo)
	$(VERBOSE)while read fil; do \
		c=`tr [:upper:] [:lower:] <<< $$$${fil:0:1}`; \
		if [ -f "$(REPO_PATH)/$$$$fil" ]; then \
			$(REPO_LINK) "$(REPO_PATH)/$$$$fil" $(REPO_DIR)/$(REPO_ID)-repo/$$$$fil; \
		elif [ -f "$(REPO_PATH)/$$$${c}/$$$$fil" ]; then \
			$(REPO_LINK) "$(REPO_PATH)/$$$${c}/$$$$fil" $(REPO_DIR)/$(REPO_ID)-repo/$$$$fil; \
		elif [ -f "$(REPO_PATH)/Packages/$$$$fil" ]; then \
			$(REPO_LINK) "$(REPO_PATH)/Packages/$$$$fil" $(REPO_DIR)/$(REPO_ID)-repo/$$$$fil; \
		elif [ -f "$(REPO_PATH)/Packages/$$$${c}/$$$$fil" ]; then \
			$(REPO_LINK) "$(REPO_PATH)/Packages/$$$${c}/$$$$fil" $(REPO_DIR)/$(REPO_ID)-repo/$$$$fil; \
		else \
			echo "Can't find $$$$fil in repo $(REPO_PATH)!"; exit 1; \
		fi; \
	done < $(CONF_DIR)/pkglist.$(REPO_ID)
	@echo "Generating $(REPO_ID) yum repo metadata, this could take a few minutes..."
	$(VERBOSE)cd $(REPO_DIR)/$(REPO_ID)-repo && $(REPO_CREATE) -g $(call FIND_COMPS,$(REPO_PATH)) .
	modmd="$(call FIND_MODMD,$(REPO_PATH))"; if [ -n "$$$$modmd" ]; then cd $(REPO_DIR)/$(REPO_ID)-repo/repodata && modifyrepo --mdtype modules "$$$$modmd" .; fi
	test -f $(YUM_CONF_ALL_FILE) || ( sed -e 's;^cachedir=.*$$$$;cachedir=$(YUM_CACHEDIR);' $(YUM_CONF_FILE).tmpl > $(YUM_CONF_ALL_FILE);\
		echo -e "[clip-repo]\\nname=clip-repo\\nbaseurl=file://$(CLIP_REPO_DIR)/\\nenabled=1\\n" >> $(YUM_CONF_ALL_FILE))
	echo -e $(YUM_CONF) >> $(YUM_CONF_ALL_FILE)
# This lets sub-makes take actions based on the full OS rver+release found in the mock repos instead of on host version
# E.g., the SELinux policy uses different spec files based on release
# Make sure YUM_CONF_ALL_FILE is a dep for any recipes that use this feature
	$(eval export OS_VER := $(strip $(shell test -f $(YUM_CONF_ALL_FILE) && repoquery -c $(YUM_CONF_ALL_FILE) --provides $$(repoquery -c $(YUM_CONF_ALL_FILE) --whatprovides "system-release") | awk ' /^system-release =/ { gsub(/-.*/,"",$$3); print $$3}')))
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
	$(VERBOSE)sed -e 's;^cachedir=.*$$$$;cachedir=$(YUM_CACHEDIR);' $(YUM_CONF_FILE).tmpl > $(YUM_CONF_FILE)
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
	@echo "The following make target is available for generating all supported installable ISOs and live CDs:"
	@echo "	all"
	@echo
	@echo "The following make targets are available for generating installable ISOs:"
	@for cd in $(INSTISOS); do echo "	$$cd"; done
	@echo
	@echo "The following make targets are available for quickly generating installable ISOs without rebuilding all of Anaconda's cruft (only use this for developer builds):"
	@for cd in $(FASTINSTISOS); do echo "	$$cd"; done
	@echo "For *-inst-iso-fast targets, you must specify a valid RHEL/CLIP ISO to use via DONOR_ISO=/home/foo/bar.iso on the command-line."
	@echo
	@echo "The following make targets are available for generating Live CDs:"
	@for cd in $(LIVECDS); do echo "	$$cd"; done
	@echo
# FIXME: re-enabled when AWS/EC2 support exists for v7
#	@echo "The following make targets are available for generating AWS :"
#	@for cd in $(AWSBUNDLES); do echo "	$$cd"; done
#	@echo
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

ifneq ($(strip $(REPO_FAILED)),)
$(info Yum repository paths do not contain a valid repo indicated by a repomd.xml somewhere)
$(error $(REPO_FAILED))
endif

# The following line calls our RPM rule template defined above allowing us to build a proper dependency list.
$(foreach RPM,$(RPMS),$(eval $(call RPM_RULE_template,$(RPM))))

# We need some packages on the build host that aren't available in EPEL, RHEL, Opt.
SRPMS := $(SRPMS) $(addprefix $(SRPM_OUTPUT_DIR)/,$(foreach RPM,$(HOST_RPMS),$(call SRPM_FROM_RPM,$(notdir $(RPM)))))

# This is a slight hack to make sure we have a valid yum repo here.
# Problem is, the repodata files are re-generated every time an PRM is built.
# This means depending on something like repo.md causes every package to be
# built every single time.  So we'll use this to fake it.
$(CLIP_REPO_DIR)/exists $(YUM_CONF_ALL_FILE):
	$(call CHECK_DEPS)
	test -f $(YUM_CONF_ALL_FILE) || ( sed -e 's;^cachedir=.*$$;cachedir=$(YUM_CACHEDIR);' $(YUM_CONF_FILE).tmpl > $(YUM_CONF_ALL_FILE);\
		echo -e "[clip-repo]\\nname=clip-repo\\nbaseurl=file://$(CLIP_REPO_DIR)/\\nenabled=1\\n" >> $(YUM_CONF_ALL_FILE))
	$(call MKDIR,$(basename $@))
	echo "Generating clip-repo metadata."; \
	$(VERBOSE)cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(call FIND_COMPS,$(REPO_PATH)) .

	@set -e; for pkg in $(PRE_ROLLED_PACKAGES); do \
           [ -f "$$pkg" ] || ( echo "Failed to find pre-rolled package: $$pkg" && exit 1 );\
           [ -h $(CLIP_REPO_DIR)/`basename $$pkg` ] && rm -f $(CLIP_REPO_DIR)/`basename $$pkg`;\
              $(REPO_LINK) $$pkg $(CLIP_REPO_DIR)|| \
	      ( echo "Failed to find pre-rolled package $$pkg - check CONFIG_BUILD and make sure you use quotes around paths with spaces." && exit 1 );\
        done
	$(VERBOSE)cd $(CLIP_REPO_DIR) && $(REPO_CREATE) -g $(call FIND_COMPS,$(REPO_PATH)) .
	touch $@

PHONIES += rpms
rpms: $(RPMS)

PHONIES += srpms
srpms: $(SRPMS)

%.src.rpm: $(MY_REPO_DEPS) $(MOCK_CONF_DIR)/$(MOCK_REL).cfg $(YUM_CONF_ALL_FILE) $(CLIP_REPO_DIR)/exists FORCE
	$(call CHECK_DEPS)
	$(call MKDIR,$(SRPM_OUTPUT_DIR))
	$(VERBOSE)OS_REL="$(call OS_REL)" $(MAKE) -C $(PKG_DIR)/$(call PKG_NAME_FROM_RPM,$(notdir $@)) srpm

PHONIES += $(LIVECDS)
$(LIVECDS):  $(CONFIG_BUILD_DEPS) $(RPMS)
	$(call CHECK_DEPS)
	$(call MAKE_LIVE_TOOLS)
	$(call MAKE_LORAX)
	$(VERBOSE)OS_REL="$(call OS_REL)" $(MAKE) -f $(KICKSTART_DIR)/Makefile -C $(KICKSTART_DIR)/"`echo '$(@)'|$(SED) -e 's/\(.*\)-live-iso/\1/'`" live-iso

PHONIES += $(FASTINSTISOS)
$(FASTINSTISOS):  $(CONFIG_BUILD_DEPS) $(RPMS)
	$(call CHECK_DEPS)
	# the script for generating fast ISOs runs the kickstart parser so, regardless of what the user told us to do, ignore it.
	$(VERBOSE)OS_REL="$(call OS_REL)" CONFIG_BUILD_CHECK_KICKSTART=n $(MAKE) DONOR_ISO=$(DONOR_ISO) -f $(KICKSTART_DIR)/Makefile -C $(KICKSTART_DIR)/"`echo '$(@)'|$(SED) -e 's/\(.*\)-inst-iso-fast/\1/'`" iso-fast

PHONIES += $(INSTISOS)
$(INSTISOS):  $(CONFIG_BUILD_DEPS) $(RPMS)
	$(call CHECK_DEPS)
	$(call MAKE_PUNGI)
	$(call MAKE_LORAX)
	$(VERBOSE)OS_REL="$(call OS_REL)" $(MAKE) -f $(KICKSTART_DIR)/Makefile -C $(KICKSTART_DIR)/"`echo '$(@)'|$(SED) -e 's/\(.*\)-inst-iso/\1/'`" iso

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

$(MOCK_CONF_DIR)/$(MOCK_REL).cfg:  $(MOCK_CONF_DIR)/$(MOCK_REL).cfg.tmpl $(CONF_DIR)/pkglist.blacklist $(CLIP_REPO_DIR)/exists $(ROOT_DIR)/Makefile
	$(call CHECK_DEPS)
	$(VERBOSE)cat $(MOCK_CONF_DIR)/$(MOCK_REL).cfg.tmpl > $@
	$(VERBOSE)echo -e $(MOCK_YUM_CONF) >> $@
	$(VERBOSE)$(SED) -i -e "s;\(config_opts\['cache_topdir'\] = '\)\(/var/cache/mock\)';\1\2/$(shell echo $$USER)';" $@
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
	$(VERBOSE)$(RM) -f $(YUM_CONF_ALL_FILE)
	$(VERBOSE)$(RM) -f $(YUM_CONF_FILE)
	$(VERBOSE)$(RM) -f $(MOCK_CONF_DIR)/$(MOCK_REL).cfg
	$(VERBOSE)$(RM) -rf $(REPO_DIR)/yumcache

PHONIES += bare-repos
bare-repos: clean-mock
	$(VERBOSE)$(RM) -f $(YUM_CONF_ALL_FILE)
	$(VERBOSE)$(RM) -rf repos/*

PHONIES += clean
clean:
	@sudo $(RM) -rf $(RPM_TMPDIR) $(TOOLS_DIR)
	@$(VERBOSE)for pkg in $(PACKAGES); do $(MAKE) -C $(PKG_DIR)/$$pkg $@; done

PHONIES += bare
bare: bare-repos clean
	for pkg in $(PACKAGES); do $(MAKE) -C $(PKG_DIR)/$$pkg $@; done
	$(VERBOSE)$(RM) -f $(addprefix $(SRPM_OUTPUT_DIR),$(SRPMS))
	$(VERBOSE)$(RM) -f $(addprefix $(OUTPUT_DIR),$(RPMS))

PHONIES += FORCE
FORCE:

# Unfortunately mock isn't exactly "parallel" friendly which sucks since we could roll a bunch of packages in parallel.
.NOTPARALLEL:
.SUFFIXES:
.PHONY: $(PHONIES) $(YUM_CONF_PHONIES)


# END RULES
######################################################
