/*
 * Soft:        Keepalived is a failover program for the LVS project
 *              <www.linuxvirtualserver.org>. It monitor & manipulate
 *              a loadbalanced server pool using multi-layer checks.
 *
 * Part:        Healthcheckrs child process handling.
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

#include "check_daemon.h"
#include "check_data.h"
#include "check_api.h"
#include "pidfile.h"
#include "signals.h"
#include "logger.h"
#include "list.h"
#include "main.h"


extern char *checkers_pidfile;
extern void init_ipvs_data(void);
extern int start_handshake(thread_t * thread);
extern void init_comm_salt(void);
extern int ipvs_init(void);

/* Daemon stop sequence */
static void
stop_check(void)
{
	/* Destroy master thread */
	signal_handler_destroy();
	thread_destroy_master(master);
	/* Stop daemon */
	pidfile_rm(checkers_pidfile);

	/*
	 * Reached when terminate signal catched.
	 * finally return to parent process.
	 */
	closelog();
	exit(0);
}


int
modprobe_ipvs(void)
{
	char *argv[] = { "/sbin/modprobe", "-s", "--", "ip_vs", NULL };
	int child;
	int status;
	int rc;

	if (!(child = fork())) {
		execv(argv[0], argv);
		exit(1);
	}

	rc = waitpid(child, &status, 0);
	if (rc < 0) {
		log_message(LOG_INFO, "IPVS: waitpid error (%s)"
				    , strerror(errno));
	}

	if (!WIFEXITED(status) || WEXITSTATUS(status)) {
		return 1;
	}

	return 0;
}


int
ipvs_start(void)
{
	log_message(LOG_DEBUG, "Initializing ipvs 2.6");
	/* Initialize IPVS module */
	if (ipvs_init()) {
		if (modprobe_ipvs() || ipvs_init()) {
			log_message(LOG_INFO, "IPVS: Can't initialize ipvs: %s",
			       ipvs_strerror(errno));
			return 0;
		}
	}
	
	return 1;
}



/* Daemon init sequence */
static void
start_check(void)
{
	/* Initialize sub-system */
	ipvs_start();

    init_ipvs_data();
	
	//handshake with peer loadbalancer then decide whether configure virtual public ip address locally
    start_handshake(NULL);
    
	//establish communication with saltstack wrapper
	init_comm_salt();




	#if 0
	init_checkers_queue();

	/* Parse configuration file */
	global_data = alloc_global_data();
	check_data = alloc_check_data();
	
	//init_data(conf_file, check_init_keywords);
	/* Virtual server mapping */
	install_keyword_root("virtual_server_group", &vsg_handler);
	install_keyword_root("virtual_server", &vs_handler);
	install_keyword("delay_loop", &delay_handler);
	install_keyword("lb_algo", &lbalgo_handler);
	install_keyword("lvs_sched", &lbalgo_handler);
	install_keyword("lb_kind", &lbkind_handler);
	install_keyword("lvs_method", &lbkind_handler);
	install_keyword("nat_mask", &natmask_handler);
	install_keyword("persistence_timeout", &pto_handler);
	install_keyword("persistence_granularity", &pgr_handler);
	install_keyword("protocol", &proto_handler);
	install_keyword("ha_suspend", &hasuspend_handler);
	install_keyword("ops", &ops_handler);
	install_keyword("virtualhost", &virtualhost_handler);

	/* Real server mapping */
	install_keyword("sorry_server", &ssvr_handler);
	install_keyword("real_server", &rs_handler);
	install_sublevel();
	install_keyword("weight", &weight_handler);
	install_keyword("uthreshold", &uthreshold_handler);
	install_keyword("lthreshold", &lthreshold_handler);
	install_keyword("inhibit_on_failure", &inhibit_handler);
	install_keyword("notify_up", &notify_up_handler);
	install_keyword("notify_down", &notify_down_handler);


	install_tcp_check_keyword();



	/* Post initializations */
	log_message(LOG_INFO, "Configuration is using : %lu Bytes", mem_allocated);


	/* Initialize IPVS topology */
	if (!init_services()) {
		stop_check();
		return;
	}

	/* Dump configuration */
	dump_global_data(global_data);
	dump_check_data(check_data);



	/* Register checkers thread */
	register_checkers_thread();
	#endif
}

/* Reload handler */
void
sighup_check(void *v, int sig)
{
}

/* Terminate handler */
void
sigend_check(void *v, int sig)
{
	if (master)
		thread_add_terminate_event(master);
}

/* CHECK Child signal handling */
void
check_signal_init(void)
{
	signal_handler_init();
	signal_set(SIGHUP, sighup_check, NULL);
	signal_set(SIGINT, sigend_check, NULL);
	signal_set(SIGTERM, sigend_check, NULL);
	signal_ignore(SIGPIPE);
}



/* CHECK Child respawning thread */
int
check_respawn_thread(thread_t * thread)
{
	pid_t pid;

	/* Fetch thread args */
	pid = THREAD_CHILD_PID(thread);

	/* Restart respawning thread */
	if (thread->type == THREAD_CHILD_TIMEOUT) {
		thread_add_child(master, check_respawn_thread, NULL,
				 pid, RESPAWN_TIMER);
		return 0;
	}

	/* We catch a SIGCHLD, handle it */
	log_message(LOG_ALERT, "Healthcheck child process(%d) died: Respawning", pid);
	start_check_child();

	return 0;
}

/* Register CHECK thread */
int
start_check_child(void)
{
	pid_t pid;
	int ret;

	/* Initialize child process */
	pid = fork();

	if (pid < 0) {
		log_message(LOG_INFO, "Healthcheck child process: fork error(%s)"
			       , strerror(errno));
		return -1;
	} else if (pid) {
	

//maybe exit here! have parent process disappear

	
		checkers_child = pid;
		log_message(LOG_INFO, "Starting Healthcheck child process, pid=%d"
			       , pid);

		/* Start respawning thread */
		thread_add_child(master, check_respawn_thread, NULL,
				 pid, RESPAWN_TIMER);
		return 0;
	}

	/* Opening local CHECK syslog channel */
	openlog("loadbalancerCHILD", LOG_PID | ((debug & 1) ? LOG_CONS : 0), LOG_DAEMON);

	/* Child process part, write pidfile */
	if (!pidfile_write(checkers_pidfile, getpid())) {
		log_message(LOG_INFO, "Healthcheck child process: cannot write pidfile");
		exit(0);
	}

	/* Create the new master thread */
	signal_handler_destroy();
	thread_destroy_master(master);
	master = thread_make_master();

	/* change to / dir */
	ret = chdir("/");
	if (ret < 0) {
		log_message(LOG_INFO, "Healthcheck child process: error chdir");
	}

	/* Set mask */
	umask(0);

	/* If last process died during a reload, we can get there and we
	 * don't want to loop again, because we're not reloading anymore.
	 */
	UNSET_RELOAD;

	/* Signal handling initialization */
	check_signal_init();

	/* Start Healthcheck daemon */
	start_check();

	/* Launch the scheduling I/O multiplexer */
	launch_scheduler();

	/* Finish healthchecker daemon process */
	stop_check();
	exit(0);
}
