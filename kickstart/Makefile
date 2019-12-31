# Copyright (C) 2011-2012 Tresys Technology, LLC
# Copyright (C) 2014-2016 Quark Security, Inc
#
# Authors: Francisco Slavin <fslavin@tresys.com>
#          Spencer Shimko <sshimko@tresys.com>
#          Spencer Shimko <spencer@quarksecurity.com>
#

NAME := $(shell basename $(CURDIR))
KS := $(CURDIR)/$(NAME).ks
INC_BASE := $(CURDIR)/..

OS_REL ?= 7.2

TARGET_ARCH ?= $(shell uname -i)

ISO_VERSION ?= 1

TMPL_CONTEXT := \
  OS_REL=$(OS_REL) \
  CONFIG_BUILD_ENABLE_DHCP=$(CONFIG_BUILD_ENABLE_DHCP) \
  CONFIG_BUILD_AWS=$(CONFIG_BUILD_AWS) \
  CONFIG_BUILD_UNCONFINED_TOOR=$(CONFIG_BUILD_UNCONFINED_TOOR) \
  CONFIG_BUILD_ENABLE_GUI=$(CONFIG_BUILD_ENABLE_GUI) \
  CONFIG_BUILD_BREAK_GUI=$(CONFIG_BUILD_BREAK_GUI)

TMPL_ARGS := $(foreach TMPL_VAR,$(TMPL_CONTEXT),--var $(TMPL_VAR))

INSTALL_INCLUDES = \
  for i in `sed -n -e 's/^%include\s\+\(.*\)$$/\1/p' $(1)`; do \
    in_file=$(INC_BASE)/$$i; \
    out_file=$(2)/$$i; \
    mkdir -p `dirname $$out_file`; \
    if [ -f $$in_file ]; then \
      cp -a $$in_file $$out_file; \
      $(VERBOSE)sed -i -e 's;\#CONFIG-BUILD-PLACEHOLDER;$(CONFIG_BUILD_BASH_VARS);' $$out_file; \
    elif [ -f $$in_file.tmpl ]; then \
      mako-render $(TMPL_ARGS) $$in_file.tmpl > $$out_file; \
      $(VERBOSE)sed -i -e 's;\#CONFIG-BUILD-PLACEHOLDER;$(CONFIG_BUILD_BASH_VARS);' $$out_file; \
    elif [[ x"`dirname $$i`" == "x/include-at-runtime" ]]; then \
      echo "ignoring runtime include file $$i"; \
    else \
      echo "missing include file $$i"; \
      exit 1; \
    fi; \
  done

ifeq ($(CONFIG_BUILD_UNCONFINED_TOOR),y)
devel_mode := y
endif

ifeq ($(CONFIG_BUILD_ENFORCING_MODE),n)
FIX_KS_ENFORCING_MODE = $(VERBOSE)sed -i -e 's/^selinux --.*/selinux --permissive/'
devel_mode := y
else
FIX_KS_ENFORCING_MODE = $(VERBOSE)sed -i -e 's/^selinux --.*/selinux --enforcing/'
endif

ifdef devel_mode
CONFIG_BUILD_ADDTL_PACKAGES += policycoreutils-devel net-tools strace gdb
endif

ROOT_DIR ?= $(CURDIR)
TMP_DIR ?= $(ROOT_DIR)/tmp
BUILD_DIR ?= $(TMP_DIR)/$(NAME)
SUPPORT_DIR ?= $(ROOT_DIR)/support
OUTPUT_DIR ?= $(ROOT_DIR)

INST_KS := $(BUILD_DIR)/$(NAME).ks
LIVE_KS := $(BUILD_DIR)/$(NAME)-live.ks
AWS_KS  := $(BUILD_DIR)/$(NAME)-aws.ks

PUNGI_OS_DIR := $(BUILD_DIR)/$(ISO_VERSION)/$(TARGET_ARCH)/os/
PUNGI_ISO_DIR := $(BUILD_DIR)/$(ISO_VERSION)/$(TARGET_ARCH)/iso/

RUN_PUNGI ?= $(SUPPORT_DIR)/runpungi.sh
PUNGI ?= $(TOOLS_DIR)/usr/bin/pungi
PUNGI_PYTHONPATH ?= $(TOOLS_DIR)/usr/lib/python2.7/site-packages/
PUNGI_ARGS := --destdir="$(BUILD_DIR)" --ver="$(ISO_VERSION)" --name="$(NAME)" --nosource --force --isfinal --cachedir="$(BUILD_DIR)/"

CHECK_VOL_ID ?= $(SUPPORT_DIR)/checkVolID.py

RUN_LIVECD ?= $(SUPPORT_DIR)/runlivecd.sh
LIVECD_CREATOR ?= $(TOOLS_DIR)/usr/bin/livecd-creator
LIVECD_PYTHONPATH ?= $(TOOLS_DIR)/usr/lib/python3.6/site-packages/
RUN_IMAGECREATE ?= $(SUPPORT_DIR)/runimagecreate.sh
IMAGE_CREATOR ?= $(TOOLS_DIR)/usr/bin/image-creator

#TODO download a specific version of these tools
#this will avoid this ugly wildcarding stuff which might break,
#and this way we'll always be using a known good version of the tools
AWS_BUNDLE_DIR := $(TMP_DIR)/$(NAME)-$(ISO_VERSION)-aws-ami
EC2_BUNDLE_IMAGE := $(EC2_AMI_TOOLS)/*/bin/ec2-bundle-image
EC2_BUNDLE_IMAGE_ARGS := --image $(BUILD_DIR)/$(NAME)-$(ISO_VERSION).img --cert $(AWS_SIGNING_CERT) --privatekey $(AWS_PRIV_KEY) -u $(AWS_ACCT_ID) --arch x86_64 --kernel $(AWS_KERNEL) -d $(AWS_BUNDLE_DIR)
AWS_MANIFEST := $(AWS_BUNDLE_DIR)/$(NAME)-$(ISO_VERSION).img.manifest.xml
EC2_UPLOAD_BUNDLE := $(EC2_AMI_TOOLS)/*/bin/ec2-upload-bundle
AWS_BUCKET ?= $(NAME)-$(ISO_VERSION)
EC2_UPLOAD_BUNDLE_ARGS := -b $(AWS_BUCKET) -a $(AWS_ACCESS_KEY_ID) -s $(AWS_ACCESS_KEY) -m $(AWS_MANIFEST) --region $(AWS_AVAIL_ZONE)
EC2_REGISTER := $(EC2_API_TOOLS)/*/bin/ec2-register
EC2_REGISTER_ARGS := -O $(AWS_ACCESS_KEY_ID) -W $(AWS_ACCESS_KEY) $(AWS_BUCKET)/$(NAME)-$(ISO_VERSION).img.manifest.xml --name "$(NAME)-$(ISO_VERSION)" --architecture x86_64 --kernel $(AWS_KERNEL) --region $(AWS_AVAIL_ZONE)
EC2_HOME := $(EC2_API_TOOLS)/ec2-api-tools-$(EC2_API_TOOLS_VER)
JAVA_HOME ?= /usr/lib/jvm/java

override LIVECD_ARGS := $(LIVECD_ARGS)

DEBUG ?= y

# These variables are usually passed in from CONFIG_BUILD to the top level Makefile.
# This will only be set here if we are running setup-ks by hand.
CONFIG_BUILD_BASH_VARS ?= export CONFIG_BUILD_PRODUCTION=n CONFIG_BUILD_ENFORCING_MODE=y CONFIG_BUILD_UNCONFINED_TOOR=y CONFIG_BUILD_SECSTATE_REMEDIATE=y ISO_VERSION=debug

# The differences between live and installable are addressed via these vars
LIVE_CONFIG_BUILD_BASH_VARS := $(CONFIG_BUILD_BASH_VARS) CONFIG_BUILD_LIVE_MEDIA=y
LIVE_CONFIG_BUILD_ADDTL_PACKAGES += $(CONFIG_BUILD_ADDTL_PACKAGES) eject
AWS_CONFIG_BUILD_BASH_VARS := $(CONFIG_BUILD_BASH_VARS) CONFIG_BUILD_AWS=y CONFIG_BUILD_VPN_ENABLE_TOOR=$(CONFIG_BUILD_VPN_ENABLE_TOOR)

# This is only useful for building out of this subdir.  The top-level Makefile passes this variable down
# pointing to the yum repos CLIP creates and manages in repos/*.  What this means is that you should
# probably just ignore this.
REPO_LINES ?= repo --name=centos --baseurl=http://mirror.centos.org/centos/$(CENTOS_VER)/os/$$basearch\nrepo --name=epel   --baseurl=http://download.fedora.redhat.com/pub/epel/$(RHEL_VER)/$$basearch

SETUP_DEPS := $(CURDIR)/../Makefile $(KS) $(shell find $(CURDIR)/../includes -type f) $(CURDIR)/variant_pkgs.mk $(shell find $(CLIP_REPO_DIRS) $(CLIP_REPO_DIR) -name repomd.xml)

INSTALL_MNT_PATH := /run/install

all: iso live-iso setup-ks


iso: $(DEPS) $(PUNGI) $(ADDTL_DEPS) setup-inst-ks check-volume-id
	@echo "Gathering things with pungi..."
	@echo "Pungi needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR); sudo $(RUN_PUNGI) "$(PUNGI_PYTHONPATH)" $(PUNGI_ARGS) -GCB -c "$(INST_KS)"
	@echo "Building ISO with pungi..."
	@echo "Pungi needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR);sudo $(RUN_PUNGI) "$(PUNGI_PYTHONPATH)" $(PUNGI_ARGS) -I -c $(INST_KS)
	$(VERBOSE)sudo rm --force $(PUNGI_ISO_DIR)/$(NAME)-netinst-$(TARGET_ARCH)-$(ISO_VERSION).iso
	$(VERBOSE)sudo mv --force $(PUNGI_ISO_DIR)/$(NAME)-*$(TARGET_ARCH)-$(ISO_VERSION).iso $(OUTPUT_DIR)/

iso-fast: setup-inst-ks
	@if [ ! -e "$(DONOR_ISO)" ]; then \
		echo "Error: DONOR_ISO $(DONOR_ISO) does not exist.  Set DONOR_ISO to the path of an existing install iso, e.g. make DONOR_ISO=foo.iso clip-minimal-inst-iso-fast."; \
		exit 1; \
	fi
	@# basic sanity check to ensure we're not going to harvest the soul of the same ISO we're building.
	@#at this point DONOR_ISO should be a full qualified path resolved in top-level makefile
	@if [ "$(ROOT_DIR)/$(NAME)-DVD-$(TARGET_ARCH)-$(ISO_VERSION)-fast.iso"  == "$(DONOR_ISO)" ]; then \
		echo "Error: DONOR_ISO and ouput ISO are the same. This doesn't make sense. Either copy the DONOR_ISO to a different filename or use a different ISO for DONOR_ISO."; \
	fi
	@echo "Creating a new ISO based on the DONOR_ISO.  Do not use in production"
	$(VERBOSE)rm -f $(ROOT_DIR)/$(NAME)-DVD-$(TARGET_ARCH)-$(ISO_VERSION)-fast.iso
	$(VERBOSE)sudo $(SUPPORT_DIR)/repack-iso.py $(DONOR_ISO) $(ROOT_DIR)/$(NAME)-DVD-$(TARGET_ARCH)-$(ISO_VERSION)-fast.iso \
		$(SUPPORT_DIR)/update-inst-iso.sh $(INST_KS) $(PUNGI_OS_DIR)$(notdir $(INST_KS)) %ISO_ROOT

live-iso: $(DEPS) $(ADDTL_DEPS) setup-live-ks
	@echo "Live CD Creator needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR);sudo $(RUN_LIVECD) $(LIVECD_PYTHONPATH) $(LIVECD_ARGS) --config="$(LIVE_KS)"
	$(VERBOSE)mv --force $(BUILD_DIR)/livecd-*.iso $(OUTPUT_DIR)/$(NAME)-$(ISO_VERSION)-live.iso

aws: $(ADDTL_DEPS) setup-aws-ks
	@echo "Image Creator needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR);sudo $(RUN_IMAGECREATE) "$(LIVECD_PYTHONPATH)" $(LIVECD_ARGS) --name=$(NAME)-$(ISO_VERSION) $(AWS_KS)
	@echo "Creating AWS bundle from image"
	mkdir -p $(AWS_BUNDLE_DIR)
	$(EC2_BUNDLE_IMAGE) $(EC2_BUNDLE_IMAGE_ARGS)
	@echo "AWS Bundle is in $(AWS_BUNDLE_DIR)"
	$(EC2_UPLOAD_BUNDLE) $(EC2_UPLOAD_BUNDLE_ARGS)
	@echo "Bundle has been uploaded to AWS"
	JAVA_HOME=$(JAVA_HOME) EC2_HOME=$(EC2_HOME) $(EC2_REGISTER) $(EC2_REGISTER_ARGS)

setup-inst-ks: $(SETUP_DEPS)
	@echo "Cleaning up after any previous builds to avoid conflicts..."
	@# Pungi doesn't do the right things when things change, and assumes the things is previously
	@# did are good to go. Bad assumption on pungi's part, which leaves us with removing everything
	$(VERBOSE)sudo rm -rf $(BUILD_DIR)
	$(VERBOSE)test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	$(VERBOSE)mkdir -p $(PUNGI_OS_DIR)
	$(VERBOSE)cp --force $(KS) $(INST_KS)
	@echo "Modifying kickstart with build variables..."
	$(VERBOSE)sed -i -e 's;#REPO-REPLACEMENT-PLACEHOLDER;$(REPO_LINES);' $(INST_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-PLACEHOLDER;$(CONFIG_BUILD_BASH_VARS);' $(INST_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-ADDTL-PACKAGES;$(shell echo "$(CONFIG_BUILD_ADDTL_PACKAGES)" | sed -e 's/ /\\n/g');' $(INST_KS)
	$(FIX_KS_ENFORCING_MODE) $(INST_KS)
	$(VERBOSE)sed -e 's/^repo/#repo/' $(INST_KS) > $(PUNGI_OS_DIR)/$(notdir $(INST_KS))
	$(VERBOSE)$(call INSTALL_INCLUDES,$(INST_KS),$(PUNGI_OS_DIR))
	$(VERBOSE)$(call INSTALL_INCLUDES,$(INST_KS),$(BUILD_DIR))
	$(VERBOSE)sed -i 's;%include\s\+\(includes/.*\);%include $(INSTALL_MNT_PATH)/repo/\1;' $(PUNGI_OS_DIR)$(notdir $(INST_KS))
ifeq ($(strip $(CONFIG_BUILD_CHECK_KICKSTART)),y)
	@echo "Validating kickstart. Any identified errors are the same that Anaconda would identify at install time."
	$(VERBOSE)$(SUPPORT_DIR)/kickstart-parser.py $(INST_KS)
else
	@echo "Build parameter CONFIG_BUILD_CHECK_KICKSTART is disabled. Skipping kickstart verification."
	@echo "Open CONFIG_BUILD and set 'CONFIG_BUILD_CHECK_KICKSTART := y' to enable this verification."
endif

check-volume-id:
	@echo "Validating Volume ID"
	$(VERBOSE)$(CHECK_VOL_ID) $(NAME) $(ISO_VERSION) $(shell arch)

setup-live-ks: $(SETUP_DEPS)
	$(VERBOSE)test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	$(VERBOSE)cp --force $(KS) $(LIVE_KS)
	@echo "Modifying kickstart with build variables..."
	$(VERBOSE)sed -i -e 's;#REPO-REPLACEMENT-PLACEHOLDER;$(REPO_LINES);' $(LIVE_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-PLACEHOLDER;$(LIVE_CONFIG_BUILD_BASH_VARS);' $(LIVE_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-ADDTL-PACKAGES;$(shell echo "$(CONFIG_BUILD_ADDTL_PACKAGES)" | sed -e 's/ /\\n/g');' $(LIVE_KS)
	$(FIX_KS_ENFORCING_MODE) $(LIVE_KS)
	$(VERBOSE)$(call INSTALL_INCLUDES,$(LIVE_KS),$(BUILD_DIR))
ifeq ($(strip $(CONFIG_BUILD_CHECK_KICKSTART)),y)
	@echo "Validating kickstart. Any identified errors are the same that Anaconda would identify at install time."
	$(VERBOSE)$(SUPPORT_DIR)/kickstart-parser.py $(LIVE_KS)
else
	@echo "Build parameter CONFIG_BUILD_CHECK_KICKSTART is disabled. Skipping kickstart verification."
	@echo "Open CONFIG_BUILD and set 'CONFIG_BUILD_CHECK_KICKSTART := y' to enable this verification."
endif

setup-aws-ks: $(SETUP_DEPS)
	$(VERBOSE)test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	$(VERBOSE)cp --force $(KS) $(AWS_KS)
	@echo "Modifying kickstart with build variables..."
	$(VERBOSE)sed -i -e 's;#REPO-REPLACEMENT-PLACEHOLDER;$(REPO_LINES);' $(AWS_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-PLACEHOLDER;$(AWS_CONFIG_BUILD_BASH_VARS);' $(AWS_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-ADDTL-PACKAGES;$(shell echo "$(CONFIG_BUILD_ADDTL_PACKAGES)" | sed -e 's/ /\\n/g');' $(AWS_KS)
	$(FIX_KS_ENFORCING_MODE) $(AWS_KS)
	$(VERBOSE)mkdir -p $(BUILD_DIR)/includes
	$(VERBOSE)cp -a $(STATIC_INC) $(BUILD_DIR)/includes/
	$(VERBOSE)$(call TMPL_INST,$(BUILD_DIR)/includes)
ifeq ($(strip $(CONFIG_BUILD_CHECK_KICKSTART)),y)
	@echo "Validating kickstart. Any identified errors are the same that Anaconda would identify at install time."
	$(VERBOSE)$(SUPPORT_DIR)/kickstart-parser.py $(AWS_KS)
else
	@echo "Build parameter CONFIG_BUILD_CHECK_KICKSTART is disabled. Skipping kickstart verification."
	@echo "Open CONFIG_BUILD and set 'CONFIG_BUILD_CHECK_KICKSTART := y' to enable this verification."
endif

clean:
	$(VERBOSE)sudo rm -rf $(BUILD_DIR)

bare: clean
	rm -rf $(TMP_DIR)

.SUFFIXES:
.PHONY: all live-iso iso clean bare setup-ks check-volume-id setup-live-ks setup-inst-ks setup-aws-ks
