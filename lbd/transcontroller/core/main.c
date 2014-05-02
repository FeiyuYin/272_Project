
/*
 * Soft:        Keepalived is a failover program for the LVS project
 *              <www.linuxvirtualserver.org>. It monitor & manipulate
 *              a loadbalanced server pool using multi-layer checks.
 *
 * Part:        Main program structure.
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

#include "main.h"
#include "signals.h"
#include "pidfile.h"
#include "logger.h"
#include "check_data.h"

/* global var */
char *conf_file = NULL;		/* Configuration file */
pid_t vrrp_child = -1;		/* VRRP child process ID */
pid_t checkers_child = -1;	/* Healthcheckers child process ID */
int linkwatch = 0;		/* Use linkwatch kernel netlink reflection */
char *main_pidfile = KEEPALIVED_PID_FILE;	/* overrule default pidfile */
char *checkers_pidfile = CHECKERS_PID_FILE;	/* overrule default pidfile */

unsigned long  lb_local_ip = 0, lb_dest_ip = 0, lb_virtual_ip =0;
extern salt_virtual_server_t *global_vs;


void init_ipvs_data(void)
{
    int size;

	size = sizeof(salt_virtual_server_t) + 20 * sizeof(salt_real_server_t);
	global_vs = (salt_virtual_server_t *)malloc(size);
	memset(global_vs, 0, size);
	global_vs->addr = lb_virtual_ip;
	global_vs->port = 80;
	global_vs->num_dests = 0;
}

/* Daemon stop sequence */
static void
stop_keepalived(void)
{
	log_message(LOG_INFO, "Stopping ");
	/* Just cleanup memory & exit */
	signal_handler_destroy();
	thread_destroy_master(master);

	pidfile_rm(main_pidfile);


	pidfile_rm(checkers_pidfile);

#ifdef _DEBUG_
	keepalived_free_final("Parent process");
#endif
}



/* SIGHUP handler */
void
sighup(void *v, int sig)
{
	/* Signal child process */
	if (vrrp_child > 0)
		kill(vrrp_child, SIGHUP);
	if (checkers_child > 0)
		kill(checkers_child, SIGHUP);
}

/* Terminate handler */
void
sigend(void *v, int sig)
{
	int status;

	/* register the terminate thread */
	thread_add_terminate_event(master);

	if (vrrp_child > 0) {
		kill(vrrp_child, SIGTERM);
		waitpid(vrrp_child, &status, WNOHANG);
	}
	if (checkers_child > 0) {
		kill(checkers_child, SIGTERM);
		waitpid(checkers_child, &status, WNOHANG);
	}
}

/* Initialize signal handler */
void
signal_init(void)
{
	signal_handler_init();
	signal_set(SIGHUP, sighup, NULL);
	signal_set(SIGINT, sigend, NULL);
	signal_set(SIGTERM, sigend, NULL);
	signal_ignore(SIGPIPE);
}

/* Usage function */
static void
usage(const char *prog)
{
	fprintf(stderr, "Usage: %s -v 56.45.32.44 -s 192.168.2.70 -d 192.168.2.140 \n", prog);
	fprintf(stderr, "  -v,             public ip address for providing internet access\n");
	fprintf(stderr, "  -s,             local ip address for load balancer to talk to peer\n");
	fprintf(stderr, "  -d,             destination ip address of peer load balancer\n");
	fprintf(stderr, "  -l,             Log messages to local console\n");
	fprintf(stderr, "  -h,             Display this help message\n");
}



/* Command line parser */
static void
parse_cmdline(int argc, char **argv)
{
	int c;

	struct option long_options[] = {
		{"log-console",       no_argument,       0, 'l'},
		{"src_ip",            required_argument, 0, 's'},
		{"dest_ip",           required_argument, 0, 'd'},
		{"virtual_ip",        required_argument, 0, 'v'},
		{"help",              no_argument,       0, 'h'},
		{0, 0, 0, 0}
	};

	while ((c = getopt_long(argc, argv, "hlv:s:d:", long_options, NULL)) != EOF) {
		switch (c) {
		case 'h':
			usage(argv[0]);
			exit(0);
			break;
		case 's':
			lb_local_ip = inet_addr(optarg);	
			break;
		case 'd':
			lb_dest_ip = inet_addr(optarg);	
			break;
		case 'v':
			lb_virtual_ip = inet_addr(optarg);	
			break;
		case 'l':
			debug |= 1;
			break;
		default:
			exit(0);
			break;
		}
	}

	if (optind < argc) {
		printf("Unexpected argument(s): ");
		while (optind < argc)
			printf("%s ", argv[optind++]);
		printf("\n");
	}

	if(lb_local_ip==0 || lb_dest_ip==0 || lb_virtual_ip==0){
		usage(argv[0]);
		exit(0);
    }
}

/* Entry point */
int
main(int argc, char **argv)
{
	/* Init debugging level */
	mem_allocated = 0;
	debug = 0;

	/*
	 * Parse command line and set debug level.
	 * bits 0..7 reserved by main.c
	 */
	parse_cmdline(argc, argv);

	openlog("loadbalancer", LOG_PID | ((debug & 1) ? LOG_CONS : 0), LOG_DAEMON);
	log_message(LOG_INFO, "Starting ");

	/* Check if keepalived is already running */
	if (keepalived_running()) {
		log_message(LOG_INFO, "daemon is already running");
		goto end;
	}

	if (debug & 1)
		enable_console_log();


	/* write the father's pidfile */
	if (!pidfile_write(main_pidfile, getpid()))
		goto end;

	/* Signal handling initialization  */
	signal_init();

	/* Create the master thread */
	master = thread_make_master();

	start_check_child();

	/* Launch the scheduling I/O multiplexer */
	launch_scheduler();

	/* Finish daemon process */
	stop_keepalived();

	/*
	 * Reached when terminate signal catched.
	 * finally return from system
	 */
end:
	closelog();
	exit(0);
}

