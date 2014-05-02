# Makefile
#
# transcontroller OpenSource project.
#
# Copyright (C) 2001-2012 Alexandre Cassen, <acassen@gmail.com>

CC	 = gcc
INCLUDES = -I../../include -I../../lib
CFLAGS	 = -g -O2  $(INCLUDES) \
	   -Wall -Wunused -Wstrict-prototypes
DEFS	 =  
COMPILE	 = $(CC) $(CFLAGS) $(DEFS)

OBJS = 	check_daemon.o check_peerlbd.o check_tcp.o comm_salt.o layer4.o main.o pidfile.o 
       
HEADERS = $(OBJS:.o=.h)

.c.o:
	$(COMPILE) -c $<

all:	$(OBJS)

clean:
	rm -f *.a *.o *~

distclean: clean
	rm -f Makefile
