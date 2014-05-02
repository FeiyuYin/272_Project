# Makefile
#
# transcontroller OpenSource project.
#
# Copyright (C) 2001-2012 Alexandre Cassen, <acassen@gmail.com>

EXEC      = transcontroller
BIN       = ../bin
KERNEL    = @KERN@
IPVS_FLAG = _WITHOUT_LVS_
VRRP_FLAG = 

prefix      = /usr/local
exec_prefix = ${prefix}
sbindir     = ${exec_prefix}/sbin
sysconfdir  = ${prefix}/etc
datarootdir = ${prefix}/share
mandir      = ${datarootdir}/man
init_dir    = $(sysconfdir)/rc.d/init.d
conf_dir    = $(sysconfdir)/transcontroller
sysconf_dir = $(sysconfdir)/sysconfig

CC = gcc
STRIP = strip
LDFLAGS =   -ldl
SUBDIRS = core

all:
	@set -e; \
	for i in $(SUBDIRS); do \
	$(MAKE) -C $$i || exit 1; done && \
	echo "Building $(BIN)/$(EXEC)" && \
	$(CC) -o $(BIN)/$(EXEC) `find $(SUBDIRS) ../lib -name '*.[oa]'` $(LDFLAGS)
	@echo ""
	@echo "Make complete"

debug:
	@set -e; \
	for i in $(SUBDIRS); do \
	$(MAKE) -C $$i || exit 1; done && \
	echo "Building $(BIN)/$(EXEC)" && \
	$(CC) -o $(BIN)/$(EXEC) `find $(SUBDIRS) ../lib -name '*.[oa]'` $(LDFLAGS) -ggdb
	@echo ""
	@echo "Make complete"

profile:
	@set -e; \
	for i in $(SUBDIRS); do \
	$(MAKE) -C $$i || exit 1; done && \
	echo "Building $(BIN)/$(EXEC)" && \
	$(CC) -o $(BIN)/$(EXEC) `find $(SUBDIRS) ../lib -name '*.[oa]'` $(LDFLAGS) -pg
	@echo ""
	@echo "Make complete"

clean:
	@set -e; \
	for i in $(SUBDIRS); do \
	$(MAKE) -C $$i clean; done
	@echo ""
	@echo "Make complete"

distclean:
	@set -e; \
	for i in $(SUBDIRS); do \
	$(MAKE) -C $$i distclean; done
	rm -f Makefile $(BIN)/$(EXEC)

mrproper: distclean
	rm -f config.*

uninstall:
	rm -f $(DESTDIR)$(sbindir)/$(EXEC)
	rm -f $(DESTDIR)$(init_dir)/transcontroller.init
	rm -f $(DESTDIR)$(sysconf_dir)/transcontroller
	rm -rf $(DESTDIR)$(sysconfdir)/transcontroller
	rm -f $(DESTDIR)$(mandir)/man/man5/transcontroller.conf.5
	rm -f $(DESTDIR)$(mandir)/man/man8/transcontroller.8

install:
	install -d $(DESTDIR)$(sbindir)
	install -m 700 $(BIN)/$(EXEC) $(DESTDIR)$(sbindir)/
	install -d $(DESTDIR)$(init_dir)
	install -m 755 etc/init.d/transcontroller.init $(DESTDIR)$(init_dir)/transcontroller
	install -d $(DESTDIR)$(sysconf_dir)
	install -m 755 etc/init.d/transcontroller.sysconfig $(DESTDIR)$(sysconf_dir)/transcontroller
	install -d $(DESTDIR)$(sysconfdir)/transcontroller/samples
	install -m 644 etc/transcontroller/transcontroller.conf $(DESTDIR)$(sysconfdir)/transcontroller/
	install -m 644 ../doc/samples/* $(DESTDIR)$(sysconfdir)/transcontroller/samples/
	install -d $(DESTDIR)$(mandir)/man5
	install -d $(DESTDIR)$(mandir)/man8
	install -m 644 ../doc/man/man5/transcontroller.conf.5 $(DESTDIR)$(mandir)/man5
	install -m 644 ../doc/man/man8/transcontroller.8 $(DESTDIR)$(mandir)/man8
