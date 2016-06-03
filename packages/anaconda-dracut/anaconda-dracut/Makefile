# Copyright (C) 2013 Cubic Corporation
#
# Authors: Spencer Shimko <spencer@quarksecurity.com>
#
MOD_PREFIX ?= $(DESTDIR)/usr/lib/dracut/modules.d
MOD_INSTDIR := $(MOD_PREFIX)/80anaconda

MOD_FILES := $(shell find 80anaconda -type f)

install:
	test -d $(MOD_INSTDIR) || install -m 755 -d $(MOD_INSTDIR)
	install -m 755 -t $(MOD_INSTDIR) $(MOD_FILES)

.PHONY: install
