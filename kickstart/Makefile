# Copyright (C) 2011-2012 Tresys Technology, LLC
# Copyright (C) 2014-215 Quark Security, Inc
#
# Authors: Francisco Slavin <fslavin@tresys.com>
#          Spencer Shimko <sshimko@tresys.com>
#          Spencer Shimko <spencer@quarksecurity.com>
#

NAME := $(shell basename $(CURDIR))
KS := $(CURDIR)/$(NAME).ks

TARGET_ARCH ?= $(shell uname -i)

ISO_VERSION ?= 1

ROOT_DIR ?= $(CURDIR)
TMP_DIR ?= $(ROOT_DIR)/tmp
BUILD_DIR ?= $(TMP_DIR)/$(NAME)
SUPPORT_DIR ?= $(ROOT_DIR)/support
OUTPUT_DIR ?= $(ROOT_DIR)

INST_KS := $(BUILD_DIR)/$(NAME)-inst.ks
LIVE_KS := $(BUILD_DIR)/$(NAME)-live.ks
AWS_KS  := $(BUILD_DIR)/$(NAME)-aws.ks

PUNGI_OS_DIR := $(BUILD_DIR)/$(ISO_VERSION)/$(TARGET_ARCH)/os/
PUNGI_ISO_DIR := $(BUILD_DIR)/$(ISO_VERSION)/$(TARGET_ARCH)/iso/

PUNGI ?= $(TOOLS_DIR)/usr/bin/pungi
PUNGI_PYTHONPATH ?= $(TOOLS_DIR)/usr/lib/python2.6/site-packages/
PUNGI_ARGS := --destdir="$(BUILD_DIR)" --ver="$(ISO_VERSION)" --name="$(NAME)" --nosource --force

CHECK_VOL_ID ?= $(SUPPORT_DIR)/checkVolID.py

LIVECD_CREATOR ?= $(TOOLS_DIR)/usr/bin/livecd-creator
LIVECD_PYTHONPATH ?= $(TOOLS_DIR)/usr/lib/python2.6/site-packages/
IMAGE_CREATOR ?= $(TOOLS_DIR)/usr/bin/image-creator

UPDATES_IMG := $(TMP_DIR)/updates.img
MK_UPDATES_IMG := $(SUPPORT_DIR)/mk-anaconda-update-img.sh
UPDATES_DIR := $(TMP_DIR)/updates

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
REPO_LINES ?= repo --name=centos --baseurl=http://mirror.centos.org/centos/6.2/os/$$basearch\nrepo --name=epel   --baseurl=http://download.fedora.redhat.com/pub/epel/$(RHEL_VER)/$$basearch

SETUP_DEPS := $(CURDIR)/../Makefile $(KS)

all: iso live-iso setup-ks


$(UPDATES_IMG): $(YUM_CONF_ALL_FILE)
	$(MK_UPDATES_IMG) $@ $(UPDATES_DIR) $(YUM_CONF_ALL_FILE)

iso: $(DEPS) $(PUNGI) $(ADDTL_DEPS) $(UPDATES_IMG) setup-inst-ks check-volume-id
	@echo "Gathering things with pungi..."
	@echo "Pungi needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR); sudo PYTHONPATH=$(PUNGI_PYTHONPATH) $(PUNGI) $(PUNGI_ARGS) -GCB -c "$(INST_KS)"
	@echo "Fixing the boot menu..."
	$(VERBOSE)sudo sed -i -e "s/^label linux$$/label $(NAME)/" \
	       -e "s/append initrd=initrd.img$$/append initrd=initrd.img ks=cdrom:$(notdir $(INST_KS))/" \
	       -e "s/or upgrade an existing system/$(NAME)/" \
	$(PUNGI_OS_DIR)/isolinux/isolinux.cfg
	@echo "Adding updates.img so this sucker boots"
	$(VERBOSE) sudo cp $(UPDATES_IMG) $(PUNGI_OS_DIR)/images/
	@echo "Building ISO with pungi..."
	@echo "Pungi needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR);sudo PYTHONPATH=$(PUNGI_PYTHONPATH) $(PUNGI) $(PUNGI_ARGS) -I -c $(INST_KS)
	$(VERBOSE)sudo mv --force $(PUNGI_ISO_DIR)/$(NAME)-$(ISO_VERSION)-*.iso $(OUTPUT_DIR)/

live-iso: $(DEPS) $(ADDTL_DEPS) setup-live-ks
	@echo "Live CD Creator needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR);sudo PYTHONPATH=$(LIVECD_PYTHONPATH) $(LIVECD_CREATOR)  $(LIVECD_ARGS) --config="$(LIVE_KS)"
	$(VERBOSE)mv --force $(BUILD_DIR)/livecd-*.iso $(OUTPUT_DIR)/$(NAME)-$(ISO_VERSION)-live.iso

aws: $(ADDTL_DEPS) setup-aws-ks
	@echo "Image Creator needs root permissions - please enter your sudo password if prompted."
	$(VERBOSE)cd $(BUILD_DIR);sudo PYTHONPATH=$(LIVECD_PYTHONPATH) $(IMAGE_CREATOR)  $(LIVECD_ARGS) --name=$(NAME)-$(ISO_VERSION) $(AWS_KS)
	@echo "Creating AWS bundle from image"
	mkdir -p $(AWS_BUNDLE_DIR)
	$(EC2_BUNDLE_IMAGE) $(EC2_BUNDLE_IMAGE_ARGS)
	@echo "AWS Bundle is in $(AWS_BUNDLE_DIR)"
	$(EC2_UPLOAD_BUNDLE) $(EC2_UPLOAD_BUNDLE_ARGS)
	@echo "Bundle has been uploaded to AWS"
	JAVA_HOME=$(JAVA_HOME) EC2_HOME=$(EC2_HOME) $(EC2_REGISTER) $(EC2_REGISTER_ARGS)

setup-inst-ks: $(SETUP_DEPS)
	@sudo rm -rf $(BUILD_DIR)/$(ISO_VERSION)/$(TARGET_ARCH)
	$(VERBOSE)test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	$(VERBOSE)mkdir -p $(PUNGI_OS_DIR)
	$(VERBOSE)cp --force $(KS) $(INST_KS)
	@echo "Modifying kickstart with build variables..."
	$(VERBOSE)sed -i -e 's;#REPO-REPLACEMENT-PLACEHOLDER;$(REPO_LINES);' $(INST_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-PLACEHOLDER;$(CONFIG_BUILD_BASH_VARS);' $(INST_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-ADDTL-PACKAGES;$(CONFIG_BUILD_ADDTL_PACKAGES);' $(INST_KS)
	$(VERBOSE)sed -e 's/^repo/#repo/' $(INST_KS) > $(PUNGI_OS_DIR)/$(notdir $(INST_KS))

check-volume-id:
	@echo "Validating Volume ID"
	$(VERBOSE)$(CHECK_VOL_ID) $(NAME) $(ISO_VERSION) $(shell arch)

setup-live-ks: $(SETUP_DEPS)
	$(VERBOSE)test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	$(VERBOSE)cp --force $(KS) $(LIVE_KS)
	@echo "Modifying kickstart with build variables..."
	$(VERBOSE)sed -i -e 's;#REPO-REPLACEMENT-PLACEHOLDER;$(REPO_LINES);' $(LIVE_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-PLACEHOLDER;$(LIVE_CONFIG_BUILD_BASH_VARS);' $(LIVE_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-ADDTL-PACKAGES;$(LIVE_CONFIG_BUILD_ADDTL_PACKAGES);' $(LIVE_KS)

setup-aws-ks: $(SETUP_DEPS)
	$(VERBOSE)test -d $(BUILD_DIR) || mkdir -p $(BUILD_DIR)
	$(VERBOSE)cp --force $(KS) $(AWS_KS)
	@echo "Modifying kickstart with build variables..."
	$(VERBOSE)sed -i -e 's;#REPO-REPLACEMENT-PLACEHOLDER;$(REPO_LINES);' $(AWS_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-PLACEHOLDER;$(AWS_CONFIG_BUILD_BASH_VARS);' $(AWS_KS)
	$(VERBOSE)sed -i -e 's;#CONFIG-BUILD-ADDTL-PACKAGES;$(AWS_CONFIG_BUILD_ADDTL_PACKAGES);' $(AWS_KS)

clean:
	$(VERBOSE)sudo rm -rf $(BUILD_DIR)

bare: clean
	rm -rf $(TMP_DIR)

.SUFFIXES:
.PHONY: all live-iso iso clean bare setup-ks check-volume-id setup-live-ks setup-inst-ks setup-aws-ks
