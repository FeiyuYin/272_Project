/*
 * Soft:        Keepalived is a failover program for the LVS project
 *              <www.linuxvirtualserver.org>. It monitor & manipulate
 *              a loadbalanced server pool using multi-layer checks.
 *
 * Part:        TCP checker.
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

#include "check_tcp.h"
#include "check_api.h"
#include "layer4.h"
#include "logger.h"


extern enum connect_result tcp_bind_connect(int fd, salt_real_server_t *rs);

extern void lbd_salt_node_up(salt_real_server_t *rs);
extern void lbd_salt_node_down(salt_real_server_t *rs);

int tcp_connect_thread(thread_t *);


int
tcp_check_thread(thread_t * thread)
{
	int status;
	salt_real_server_t *rs = THREAD_ARG(thread);
	struct in_addr in;

	in.s_addr = rs->ipaddr;

	status = tcp_socket_state(thread->u.fd, thread, tcp_check_thread);

	/* If status = connect_success, TCP connection to remote host is established.
	 * Otherwise we have a real connection error or connection timeout.
	 */
	if (status == connect_success) {
		close(thread->u.fd);

		log_message(LOG_ERR, "TCP connection to [%s]:%d success.", 
			          inet_ntoa(in), rs->port);
		
		lbd_salt_node_up(rs);

	} else {
		log_message(LOG_ERR, "TCP connection to [%s]:%d fail." 
	         , inet_ntoa(in), rs->port);
		
		lbd_salt_node_down(rs);

	}

	/* Register next timer checker */
	if (status != connect_in_progress)
		thread_add_timer(thread->master, tcp_connect_thread, NULL, BOOTSTRAP_DELAY);
	return 0;
}

int
tcp_connect_thread(thread_t * thread)
{
	int fd;
	int status;
	salt_real_server_t *rs = THREAD_ARG(thread);

	
	if ((fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
		log_message(LOG_INFO, "TCP connect fail to create socket. Rescheduling.");
 		thread_add_timer(thread->master, tcp_connect_thread, rs, BOOTSTRAP_DELAY); 
		return 0;
	}

	status = tcp_bind_connect(fd, rs);

	/* handle tcp connection status & register check worker thread */
	if(tcp_connection_state(fd, status, thread, tcp_check_thread, BOOTSTRAP_DELAY)) {
		close(fd);
		log_message(LOG_INFO, "TCP socket bind failed. Rescheduling.");
		thread_add_timer(thread->master, tcp_connect_thread, rs, BOOTSTRAP_DELAY);
	}
 
	return 0;
}
