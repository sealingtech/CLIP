prefix=$(DESTDIR)
bindir=$(prefix)/usr/bin
initdir=$(prefix)/etc/init\.d/

all: add_ss_user 

INIT_SCRIPTS=configure-strongswan
HELPER_PROGS=add_vpn_user.sh gen_passwd.sh gen_subj.sh gen_word.sh strongswan_login.py

#TODO more hardened flags?
CFLAGS := -Werror -Wextra -Wall

add_ss_user: add_ss_user.c
	$(CC) $(CFLAGS) -o $@ $^

install: add_ss_user $(HELPER_PROGS) $(INIT_SCRIPTS)
	mkdir -p $(bindir)
	mkdir -p $(initdir)
	install -m 4755 add_ss_user $(bindir)
	install -m 755 $(HELPER_PROGS) $(bindir)
	install -m 755 $(INIT_SCRIPTS) $(initdir)

clean:
	rm -rf add_ss_user

.PHONY: install
