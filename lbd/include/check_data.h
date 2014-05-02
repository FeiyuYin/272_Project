/*
 * Soft:        Keepalived is a failover program for the LVS project
 *              <www.linuxvirtualserver.org>. It monitor & manipulate
 *              a loadbalanced server pool using multi-layer checks.
 *
 * Part:        Healthcheckers dynamic data structure definition.
 *
 * Author:      Alexandre Cassen, <acassen@linux-vs.org>
 *
 *              This program is distributed in the hope that it will be useful,
 *              but WITHOUT ANY WARRANTY; without even the implied warranty of
 *              MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *              See the GNU General Public License for more details.
 *
 *              This program is free software; you can redistribute it and/or
 *              modify it under the terms of the GNU General Public License
 *              as published by the Free Software Foundation; either version
 *              2 of the License, or (at your option) any later version.
 *
 * Copyright (C) 2001-2012 Alexandre Cassen, <acassen@gmail.com>
 */

#ifndef _CHECK_DATA_H
#define _CHECK_DATA_H

/* system includes */
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <syslog.h>
#include <arpa/inet.h>
//#include <openssl/ssl.h>

#include <linux/ip_vs.h>
//  #define SCHED_MAX_LENGTH IP_VS_SCHEDNAME_MAXLEN

/* local includes */
#include "list.h"
#include "vector.h"
#include "timer.h"
#include "scheduler.h"
/* Typedefs */
typedef unsigned int checker_id_t;

/* Daemon dynamic data structure definition */
#define MAX_TIMEOUT_LENGTH		5
#define KEEPALIVED_DEFAULT_DELAY	(60 * TIMER_HZ) 


typedef struct _salt_real_server {
	int ipaddr;
	int port;
	int mark;
	int upgrade_state;  //1:allow group 1 upgrade, 2: allow group 2 upgrade,  3, tcp check dest is ok, add rs into kernel
	int dest_rate;
	thread_t *thread;
	int state; //0: unkown, 1: active and add rs to kernel, 2: down and remove rs from kernel
}salt_real_server_t;

typedef struct _salt_virtual_server {
	int			addr;		/* virtual address */
	int			port;

	/* number of real servers */
	uint32_t    num_dests;

	/* the real servers */
	salt_real_server_t	entrytable[0];
}salt_virtual_server_t;





#endif
