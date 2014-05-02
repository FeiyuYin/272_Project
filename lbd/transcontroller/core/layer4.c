/*
 * Soft:        Keepalived is a failover program for the LVS project
 *              <www.linuxvirtualserver.org>. It monitor & manipulate
 *              a loadbalanced server pool using multi-layer checks.
 *
 * Part:        Layer4 checkers handling. Register worker threads &
 *              upper layer checkers.
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

#include "layer4.h"
#include "check_api.h"
#include "logger.h"
extern unsigned long  lb_local_ip;

enum connect_result
tcp_bind_connect(int fd, salt_real_server_t *rs)
{

	struct sockaddr_in srcaddr, dstaddr;
	struct linger li = { 0 };
	socklen_t addrlen;
	int ret;
	int val;

	/* free the tcp port after closing the socket descriptor */
	li.l_onoff = 1;
	li.l_linger = 0;
	setsockopt(fd, SOL_SOCKET, SO_LINGER, (char *) &li, sizeof (struct linger));

	/* Make socket non-block. */
	val = fcntl(fd, F_GETFL, 0);
	fcntl(fd, F_SETFL, val | O_NONBLOCK);


	/* Bind socket */
	srcaddr.sin_family      =  AF_INET;
    srcaddr.sin_addr.s_addr =  lb_local_ip;
	addrlen = sizeof(srcaddr);
	if (bind(fd, (struct sockaddr *) &srcaddr, addrlen) != 0){
		log_message(LOG_ERR, "tcp binding error: %s", ipvs_strerror(errno));
		return connect_error;
	}

	/* Set remote IP and connect */
	dstaddr.sin_family      =  AF_INET;
    dstaddr.sin_port        =  htons(rs->port);
    dstaddr.sin_addr.s_addr =  rs->ipaddr;
	addrlen = sizeof(dstaddr);
	ret = connect(fd, (struct sockaddr *) &dstaddr, addrlen);

	/* Immediate success */
	if (ret == 0) {
		fcntl(fd, F_SETFL, val);
		return connect_success;
	}

	/* If connect is in progress then return 1 else it's real error. */
	if (ret < 0) {
		if (errno != EINPROGRESS)
			return connect_error;
	}

	/* restore previous fd args */
	fcntl(fd, F_SETFL, val);
	return connect_in_progress;
}


enum connect_result
tcp_socket_state(int fd, thread_t * thread, int (*func) (thread_t *))
{
	int status;
	socklen_t addrlen;
	int ret = 0;
	timeval_t timer_min;

	/* Handle connection timeout */
	if (thread->type == THREAD_WRITE_TIMEOUT) {
		close(thread->u.fd);
		return connect_timeout;
	}

	/* Check file descriptor */
	addrlen = sizeof(status);
	if (getsockopt(thread->u.fd, SOL_SOCKET, SO_ERROR, (void *) &status, &addrlen) < 0)
		ret = errno;

	/* Connection failed !!! */
	if (ret) {
		close(thread->u.fd);
		return connect_error;
	}

	/* If status = 0, TCP connection to remote host is established.
	 * Otherwise register checker thread to handle connection in progress,
	 * and other error code until connection is established.
	 * Recompute the write timeout (or pending connection).
	 */
	if (status == EINPROGRESS) {
		timer_min = timer_sub_now(thread->sands);
		thread_add_write(thread->master, func, THREAD_ARG(thread),
				 thread->u.fd, timer_long(timer_min));
		return connect_in_progress;
	} else if (status != 0) {
		close(thread->u.fd);
		return connect_error;
	}

	return connect_success;
}

int
tcp_connection_state(int fd, enum connect_result status, thread_t * thread,
		     int (*func) (thread_t *), long timeout)
{
	salt_real_server_t *rs = THREAD_ARG(thread);

	switch (status) {
	case connect_success:
		thread_add_write(thread->master, func, rs, fd, timeout);
		return 0;

		/* Checking non-blocking connect, we wait until socket is writable */
	case connect_in_progress:
		thread_add_write(thread->master, func, rs, fd, timeout);
		return 0;

	default:
		return 1;
	}
}
