
#include "comm_salt.h"
#include <sys/types.h>
#include <sys/socket.h>
#include "check_api.h"
#include "logger.h"
#include <unistd.h>


struct lbd_msg {
	int type;  //0: state unkown, 1: i am master, 2:i am slave, 3: heartbeat
	int current_master; //1: assigned virtual public ip address already, 0: not yet
};

int peer_sock_fd = -1;
int master_state = 0;
int least_ip = 0;
int exchang_heartbeat = 0;
int unreachable_times = 0;

extern unsigned long  lb_local_ip;
extern unsigned long  lb_dest_ip;
extern unsigned long  lb_virtual_ip;

void become_master(void);
void delete_master_info(void);
int lbd_rcvmsg_peer(thread_t * thread);
void send_msg_peer(int type);
int start_handshake(thread_t * thread);
extern void notify_salt_state(int state);


void become_master(void)
{
	if(master_state == 1)
		return;

	//TBD
    //config virtual public ip addr

	
	notify_salt_state(1);

	master_state = 1;
}

void delete_master_info(void)
{
	if(master_state == 0)
		return;

	//TBD
    //delete virtual public ip addr
    

	notify_salt_state(0);
	master_state = 0;
}

int lbd_rcvmsg_peer(thread_t * thread)
{
    struct lbd_msg msg;
	int peer_reachable = 0;
	
    if(exchang_heartbeat)
		send_msg_peer(3);
		
	while(1)
	{
		if(recv(peer_sock_fd, &msg, sizeof(msg), 0) == -1)
			break;
		
		peer_reachable ++;

		switch(msg.type) {
			case 0:
				if(least_ip || master_state)
				{
					send_msg_peer(1); // to be a master or already a master
				}
				else
					send_msg_peer(2); //to be a  slave
				break;
			case 1:
                if(msg.current_master == 1 && master_state == 1) //i am master too, problem exist
            	{
	            	//delete virtual public ip, and reselect master
	            	delete_master_info();
	            	send_msg_peer(0);  //reselect master
            	}
				else if(msg.current_master == 0 && master_state == 1) 
				{
					// i am already a master, dont allow peer to become a master
					send_msg_peer(1);
				}
				else
				{
					send_msg_peer(2);
					exchang_heartbeat = 1;
				}
                
				break;
			case 2:
				if(master_state == 0 && least_ip == 0) //i am slave too, problem exist
					send_msg_peer(0);  //reselect master
                else
            	{
	            	become_master();
					exchang_heartbeat = 1;
            	}
				break;
			case 3:
				if(master_state == msg.current_master) //two slave or two master at same time
				{
				    delete_master_info();
					send_msg_peer(0);  //reselect master
					exchang_heartbeat = 0;
				}
				exchang_heartbeat = 1;
				break;
            default:
				log_message(LOG_ERR, "not support this type in lbd: %d", msg.type);
		}
	}


	if(!peer_reachable)
        unreachable_times++;

	//lose contact with peer for 2 seconds
	if(unreachable_times == 2)
	{
		become_master();
		send_msg_peer(0);
		unreachable_times = 0;
	}
	
	thread_add_read(master, lbd_rcvmsg_peer, 0, peer_sock_fd, BOOTSTRAP_DELAY);

	return 1;
}


void send_msg_peer(int type)
{
	struct lbd_msg msg;
	int ret;
	
	msg.current_master = master_state;
	msg.type = 0;
	ret = send(peer_sock_fd, &msg, sizeof(struct lbd_msg), 0);
	if(ret == sizeof(struct lbd_msg))
		log_message(LOG_ERR, "send msg to peer error: %s", ipvs_strerror(errno));
}

int start_handshake(thread_t * thread)
{
    //peer sockaddr_in
    struct sockaddr_in srcaddr;  
    struct sockaddr_in dstaddr;  
    int                sock_fd;
    int                flags;
    int ret = -1;

	sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if(sock_fd == -1)
    { 
        log_message(LOG_ERR, "not able to create socket: %s", ipvs_strerror(errno));
        goto thread_add;
    }

	srcaddr.sin_family      =  AF_INET;
    srcaddr.sin_port        =  htons(54238);
    srcaddr.sin_addr.s_addr =  lb_local_ip;

    if(bind(sock_fd,(struct sockaddr *)&srcaddr, sizeof(srcaddr)) == -1)
    {
        close(sock_fd);
        log_message(LOG_ERR, "binding error: %s", ipvs_strerror(errno));
        goto thread_add;
    }

	//set nonblock
	flags = fcntl(sock_fd, F_GETFL, 0);
	fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

	
	dstaddr.sin_family		=  AF_INET;
	dstaddr.sin_port		=  htons(54238);
	dstaddr.sin_addr.s_addr =  lb_dest_ip;
	ret = connect(sock_fd, (struct sockaddr *)&dstaddr, sizeof(dstaddr));

thread_add:
    if(ret < 0)
		thread_add_timer(master, start_handshake, NULL, BOOTSTRAP_DELAY);
	else
	{
		peer_sock_fd = sock_fd;
		if(lb_dest_ip > lb_local_ip)
			least_ip = 1;
        send_msg_peer(0);
		thread_add_read(master, lbd_rcvmsg_peer, 0, sock_fd, BOOTSTRAP_DELAY);
	}

	return 1;
}

