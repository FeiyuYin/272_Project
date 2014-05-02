
#include <unistd.h>
#include "comm_salt.h"
#include <sys/types.h>
#include <sys/socket.h>
#include "check_api.h"
#include <linux/ip_vs.h>
#include "logger.h"


uint8_t rcvbuff[2048];
uint8_t msgbuff[2048];
int stats_timer = 0;
int salt_sock_fd = -1;
uint8_t sndbuff[2048];
int ipvs_vs_config = 0;
int upgrade_phase = 0;

int sockfd = -1;

extern unsigned long  lb_local_ip;
extern unsigned long lb_virtual_ip;
extern int master_state;

salt_virtual_server_t *global_vs;


extern int tcp_connect_thread(thread_t * thread);
int lbd_rcvmsg_salt(thread_t * thread);
void handle_salt_msg(salt_node_list_t *msg);
void notify_salt_state(int state);
void ipvs_config_vs_8080_2_80(void);
void ipvs_config_vs(void);
void ipvs_del_vs(void);
void construct_vs(struct ip_vs_service_user *vs, int port);
void ipvs_salt_add_rs(salt_real_server_t *rs);
void del_from_rs_list(salt_real_server_t *rs);
int add_to_rs_list(salt_ip_node_t *rs);
void handle_salt_ipaddr(salt_node_list_t *msg);
void lbd_salt_node_up(salt_real_server_t *rs);
void lbd_salt_node_down(salt_real_server_t *rs);
void ipvs_salt_del_rs(salt_real_server_t *rs, int flag);
void handle_salt_upgrade_rest(salt_node_list_t *msg);
int upgrade_phase2(thread_t * thread);
int protect_ipaddr_no_change(thread_t * thread);
void handle_salt_upgrade_done(void);
void handle_salt_upgrade(salt_node_list_t *msg);
void set_node_upgrade(int index, int val);
int check_node_upgrade(int index, int val);
void lbd_request_ipaddr(void);
int check_ipaddr_against_vs(salt_node_list_t *msg);
void handle_salt_stat(void);
int ipvs_salt_get_dests(thread_t * thread);
void set_ip_mark(int index, int val);
int check_ipaddr_exist(int ipaddr);
void start_salt_stat(void);
void init_comm_salt(void);
int ipvs_init(void);
int start_comm_salt(thread_t * thread);




int lbd_rcvmsg_salt(thread_t * thread)
{
    //int sock_fd = (int)THREAD_ARG(thread);
    int ret;
    
    while(1)
    {
        ret = recvfrom(salt_sock_fd, rcvbuff, 2048, 0, NULL, NULL);
        if(ret == -1)
        {
            break;
        }

        handle_salt_msg((salt_node_list_t *)rcvbuff);
    }


	thread_add_read(master, lbd_rcvmsg_salt, 0, salt_sock_fd, BOOTSTRAP_DELAY);

	return 1;
}

void handle_salt_msg(salt_node_list_t *msg)
{

	log_message(LOG_ERR, "receive msg from salt, %d", msg->type);

	switch(msg->type) {
		case SALT_CONFIG_IPADDR:
			handle_salt_ipaddr(msg);
	        break;
		case SALT_REQUEST_STATS:
			handle_salt_stat();
	        break;
		case SALT_UPGRADE_WEBAPP:
			handle_salt_upgrade(msg);
			break;
		case SALT_UPGRADE_CONTINUE:
			handle_salt_upgrade_rest(msg);
			break;
		case SALT_UPGRADE_DONE:
			handle_salt_upgrade_done();
			break;
		default:
			log_message(LOG_ERR, "not support type, %d", msg->type);
	}

	
}

void notify_salt_state(int state)
{
    int len;
    salt_node_list_t *msg = (salt_node_list_t *)sndbuff;
	msg->node_num = 0;

	if(state == 0) //slave
		msg->type = SALT_IS_SLAVE;
	else 
		msg->type = SALT_IS_MASTER;
	
	len = send(salt_sock_fd, msg, sizeof(salt_node_list_t), 0);
    if (len != sizeof(salt_node_list_t))
		log_message(LOG_ERR, "sned partial data to salt, org len=%d, sending len=%d", sizeof(salt_node_list_t), len);

    if(state == 1) //request ip addr to kick off
	{
		lbd_request_ipaddr();
        ipvs_config_vs();
	}
	else
		ipvs_del_vs();

    //for salt wrapper webapp
	ipvs_config_vs_8080_2_80();

}

void ipvs_config_vs_8080_2_80(void)
{
	struct ip_vs_service_user vs; 
	struct ip_vs_service_user *vs_rs; 
	struct ip_vs_dest_user *rs;
	
    int len;

	
    if(ipvs_vs_config == 1)
		return;

    len = sizeof(struct ip_vs_service_user) + sizeof(struct ip_vs_dest_user);
    vs_rs = (struct ip_vs_service_user *)malloc(len);
	memset(vs_rs, 0, len);
	
	construct_vs(&vs, 8080);
	if(setsockopt(sockfd, IPPROTO_IP, IP_VS_SO_SET_ADD, (char *)&vs,
			  sizeof(struct ip_vs_service_user)))
		  log_message(LOG_ERR, "fail to config vs, %s", ipvs_strerror(errno));
 	else {
		construct_vs(vs_rs, 8080); 
		rs = (struct ip_vs_dest_user *)(vs_rs + 1);
		rs->addr = lb_local_ip;
		rs->port = 80;
		rs->conn_flags = IP_VS_CONN_F_MASQ;
		
		if(setsockopt(sockfd, IPPROTO_IP, IP_VS_SO_SET_ADDDEST,
				  (char *)vs_rs, len))
			 log_message(LOG_ERR, "fail to add rs, %s", ipvs_strerror(errno)); 
	}
}

void ipvs_config_vs(void)
{ 
	struct ip_vs_service_user vs; 

    if(ipvs_vs_config == 1)
		return;

	construct_vs(&vs, 80);

	if(setsockopt(sockfd, IPPROTO_IP, IP_VS_SO_SET_ADD, (char *)&vs,
			  sizeof(struct ip_vs_service_user)))
		  log_message(LOG_ERR, "fail to config vs, %s", ipvs_strerror(errno));
	else
		ipvs_vs_config = 1;
	
}

void ipvs_del_vs(void)
{ 
	struct ip_vs_service_user vs; 

	construct_vs(&vs, 80);

	if(setsockopt(sockfd, IPPROTO_IP, IP_VS_SO_SET_DEL, (char *)&vs,
			  sizeof(struct ip_vs_service_user)))
		  log_message(LOG_ERR, "fail to del vs, %s", ipvs_strerror(errno));

	ipvs_vs_config = 0;
}


void construct_vs(struct ip_vs_service_user *vs, int port)
{
	memset(vs, 0, sizeof(struct ip_vs_service_user));
    vs->protocol = IPPROTO_TCP;
	vs->port = (unsigned short)port;
	vs->addr = lb_virtual_ip;
	strcpy(vs->sched_name, "rr");
	vs->timeout = 3;
	vs->netmask = 0xffffffff;
}


void ipvs_salt_add_rs(salt_real_server_t *rs)
{
	struct ip_vs_service_user *vs_rs; 
	struct ip_vs_dest_user *t_rs;
	int len;

    len = sizeof(struct ip_vs_service_user) + sizeof(struct ip_vs_dest_user);
    vs_rs = (struct ip_vs_service_user *)malloc(len);	
	memset(vs_rs, 0, len);
	if(ipvs_vs_config == 0 && master_state == 1)
		ipvs_config_vs();

    construct_vs(vs_rs, 80); 
	t_rs = (struct ip_vs_dest_user *)(vs_rs + 1);

	t_rs->addr = rs->ipaddr;
	t_rs->port = rs->port;
	t_rs->conn_flags = IP_VS_CONN_F_MASQ;

	if(setsockopt(sockfd, IPPROTO_IP, IP_VS_SO_SET_ADDDEST,
			  (char *)vs_rs, len))
		 log_message(LOG_ERR, "fail to add rs, %s", ipvs_strerror(errno)); 
	else
		rs->state = 1;
}


void del_from_rs_list(salt_real_server_t *rs)
{
    int index = check_ipaddr_exist(rs->ipaddr);
    int i;

	if( index == -1)
		return;

    thread_cancel(global_vs->entrytable[index].thread);
	
	for(i = index; i < global_vs->num_dests-1; i++){
		global_vs->entrytable[i].ipaddr = global_vs->entrytable[i+1].ipaddr;
		global_vs->entrytable[i].port	= global_vs->entrytable[i+1].port;
	}

	global_vs->num_dests--;

}


int add_to_rs_list(salt_ip_node_t *rs)
{
    if(global_vs->num_dests >= 20){
		log_message(LOG_ERR, "extend maximum rs number");
		return -1;
	}
	
    if (check_ipaddr_exist(rs->ipaddr) != -1) 
		return -1;

	salt_real_server_t *index = &global_vs->entrytable[global_vs->num_dests];
	index->ipaddr = rs->ipaddr;
	index->port = rs->port;
	index->mark = 1;
	index->thread = thread_add_timer(master, tcp_connect_thread, &index, 0);
	
	global_vs->num_dests++;
	return (global_vs->num_dests-1);
}


void handle_salt_ipaddr(salt_node_list_t *msg)
{
    int  i =0;
	salt_ip_node_t *rs;
	int index;

    //dont modify node info while upgrading
    if (upgrade_phase)
	{
	    log_message(LOG_ERR, "not allow to chang ip addr when upgrading");  
		return;
	}
	
	for(; i < msg->node_num; i++)
	{
		rs = &msg->entry[i];
		index = check_ipaddr_exist(rs->ipaddr);
		if(index == -1)
		{
		    add_to_rs_list(rs);
		}
		else
			set_ip_mark(index,1);
	}

    //delete unused ip
	for(i = global_vs->num_dests-1; i >=0 ; i--)
	{
        if(global_vs->entrytable[i].mark == 1){
			set_ip_mark(i, 0);
			continue;
    	}

		ipvs_salt_del_rs(&global_vs->entrytable[i], 1);
	}
	
}



void lbd_salt_node_up(salt_real_server_t *rs)
{
    if (rs->state == 1)
		return;
	
	//group 1 webapp should go up after receive SALT_UPGRADE_CONTINUE from salt to make sure all webapp in group 1 have upgraded
	if(rs->upgrade_state == 1 && upgrade_phase < 2)  
	    return;

	//group 2 webapp should go up after receive SALT_UPGRADE_DONE from salt to make sure all webapp in group 2 have upgraded
	if(rs->upgrade_state == 2)  
	    return;

	
	ipvs_salt_add_rs(rs);
	log_message(LOG_ERR, "node is up, push rs into kernel");
	
	if(rs->upgrade_state == 1)
		rs->upgrade_state = 3;
}

void lbd_salt_node_down(salt_real_server_t *rs)
{

    if (rs->state == 2)
		return;
	
	
	ipvs_salt_del_rs(rs, 0);	
	log_message(LOG_ERR, "node is down, delete rs from kernel");  
}


void ipvs_salt_del_rs(salt_real_server_t *rs, int flag)
{
	struct ip_vs_service_user *vs_rs; 
	struct ip_vs_dest_user *t_rs;
	int len;


    len = sizeof(struct ip_vs_service_user) + sizeof(struct ip_vs_dest_user);
    vs_rs = (struct ip_vs_service_user *)malloc(len);	
    memset(vs_rs, 0, len);
    construct_vs(vs_rs, 80); 

	t_rs = (struct ip_vs_dest_user *)(vs_rs + 1);
	t_rs->addr = rs->ipaddr;
	t_rs->port = rs->port;

	if(setsockopt(sockfd, IPPROTO_IP, IP_VS_SO_SET_DELDEST,
			  (char *)vs_rs, len))
		 log_message(LOG_ERR, "fail to del rs, %s", ipvs_strerror(errno));  
	else 
		rs->state = 2;

	if(flag)
		del_from_rs_list(rs);
	
}

void handle_salt_upgrade_rest(salt_node_list_t *msg)
{
    //int i, ret, len;
	//salt_ip_node_t *rs;


    if(upgrade_phase!= 1)
		return;
	
	if(msg->node_num != 0 && !check_ipaddr_against_vs(msg))
		return;

	upgrade_phase = 2;
	
	memcpy(msgbuff, sndbuff, sizeof(salt_node_list_t) + msg->node_num * sizeof(salt_ip_node_t));
    upgrade_phase2(NULL);
}


int upgrade_phase2(thread_t * thread)
{
    int i, ret, len, index;
	salt_ip_node_t *rs;
	salt_node_list_t *msg = (salt_node_list_t *)msgbuff;
	salt_real_server_t *g_rs;

    if(upgrade_phase == 0){
		log_message(LOG_ERR, "upgrade process timeout, cancel this upgrade.");
		return 0;
	}
	
	//at least one new upgraded node is available, then can continue to upgrade the rest nodes
	for(i = 0; i < global_vs->num_dests; i++)
	{
		if(check_node_upgrade(i, 3)) 
		{
			upgrade_phase = 3;
			break;
		}
	}

	if(upgrade_phase != 3){
		log_message(LOG_ERR, "no active node so far among upgraded nodes, wait for up");
		thread_add_timer(master, upgrade_phase2, NULL, BOOTSTRAP_DELAY);
		return 0;
	}

	for(i = 0; i < msg->node_num; i++)
	{
		rs = &msg->entry[i];
		index = check_ipaddr_exist(rs->ipaddr);
		g_rs = &global_vs->entrytable[index];

		if(check_node_upgrade(index, 3) || check_node_upgrade(index, 1)){
			rs->dispathing_rate = 0; //avoid invalid data
			continue;
		}
					
		ipvs_salt_del_rs(g_rs, 0);
		set_node_upgrade(index, 2); //group 2 under upgrading
		rs->dispathing_rate = 0xFFF3; //allow upgrade 			 
	}

	len = sizeof(salt_node_list_t) + msg->node_num * sizeof(salt_ip_node_t);
	ret = send(salt_sock_fd, msg, len, 0);
	if (len != ret)
		log_message(LOG_ERR, "sned partial upgrade data to salt, org len=%d, sending len=%d", sizeof(salt_node_list_t), len);   	
	
	return 1;	
}

int protect_ipaddr_no_change(thread_t * thread)
{
    int i = 0;
	
    //done upgrade in lbd
	for(i = 0; i < global_vs->num_dests; i++)
	{
		set_node_upgrade(i, 0); 
	}

	upgrade_phase = 0;

	return 1;
}

void handle_salt_upgrade_done(void)
{
	protect_ipaddr_no_change(NULL);
}

void handle_salt_upgrade(salt_node_list_t *msg)
{
    int i, ret, len, index;
	int active_xor = 0, inactive_xor = 0;
	salt_ip_node_t *rs;
	salt_real_server_t *g_rs;

	
	if(msg->node_num != 0 && !check_ipaddr_against_vs(msg))
		return;

    upgrade_phase = 1;
	thread_add_timer(master, protect_ipaddr_no_change, NULL, 20 * BOOTSTRAP_DELAY);


	for(i = 0; i < msg->node_num; i++)
	{
		rs = &msg->entry[i];
		index = check_ipaddr_exist(rs->ipaddr);
		g_rs = &global_vs->entrytable[index];
		
        if(g_rs->state == 1 && active_xor == 0){
			active_xor = 1;
			ipvs_salt_del_rs(g_rs, 0);
			set_node_upgrade(index, 1); //group 1 under upgrading
			rs->dispathing_rate = 0xFFF3; //allow upgrade 
	        continue;
        }
		else if(g_rs->state == 1 && active_xor == 1){
			active_xor = 0;
			rs->dispathing_rate = 0;//avoid invalid data
			continue;
		}

        if(g_rs->state == 2 && inactive_xor == 0){
			inactive_xor = 1;
			set_node_upgrade(index, 1); //group 1 under upgrading
			rs->dispathing_rate = 0xFFF3; //allow upgrade 
        }
		else if(g_rs->state == 2 && inactive_xor == 1){
			inactive_xor = 0; 
			rs->dispathing_rate = 0;//avoid invalid data
		}
		
	}

    len = sizeof(salt_node_list_t) + msg->node_num * sizeof(salt_ip_node_t);
	ret = send(salt_sock_fd, msg, len, 0);
	if (len != ret)
		log_message(LOG_ERR, "sned partial upgrade data to salt, org len=%d, sending len=%d", sizeof(salt_node_list_t), len);
		
}


void set_node_upgrade(int index, int val)
{
    if(index >= 20){
		return;
	}

	global_vs->entrytable[index].upgrade_state = val;
}

int check_node_upgrade(int index, int val)
{
    if(index >= 20){
		return -1;
	}

	return global_vs->entrytable[index].upgrade_state == val;
}


void lbd_request_ipaddr(void)
{
	int  len;
    salt_node_list_t *msg = (salt_node_list_t *)sndbuff;
	
	msg->node_num = 0;
	msg->type = SALT_REQUEST_IPADDR;
	len = send(salt_sock_fd, msg, sizeof(salt_node_list_t), 0);
	if (len != sizeof(salt_node_list_t))
		log_message(LOG_ERR, "sned partial SALT_REQUEST_IPADDR data to salt, org len=%d, sending len=%d", sizeof(salt_node_list_t), len);
}

int check_ipaddr_against_vs(salt_node_list_t *msg)
{
	int  i =0;
	salt_ip_node_t *rs;
	int index;

    if(msg->node_num != global_vs->num_dests){
		log_message(LOG_ERR, "number of nodes are not equal");  
		return 0;
	}

	for(; i < msg->node_num; i++)
	{
		rs = &msg->entry[i];
		index = check_ipaddr_exist(rs->ipaddr);
		if(index == -1)
		{
			log_message(LOG_ERR, "ip addr not stored in vs, request new ip addr"); 
			lbd_request_ipaddr();
			return 0;
		}
	}

	return 1;
}


void handle_salt_stat(void)
{
	salt_node_list_t *msg = (salt_node_list_t *)sndbuff;
    int len, ret;
	int i;

	
	msg->type = SALT_DISPATCHING_STATS;
	msg->node_num = global_vs->num_dests;

	for(i=0; i < global_vs->num_dests; i++)
	{
		msg->entry[i].dispathing_rate = global_vs->entrytable[i].dest_rate;
		msg->entry[i].port = global_vs->entrytable[i].port;
		msg->entry[i].ipaddr = global_vs->entrytable[i].ipaddr;
	}

    len = sizeof(salt_node_list_t) + i * sizeof(salt_ip_node_t);
	
	ret = send(salt_sock_fd, msg, len, 0);
    if (ret != len)
		log_message(LOG_ERR, "sned partial SALT_DISPATCHING_STATS data to salt, org len=%d, sending len=%d", len, ret);

}

int ipvs_salt_get_dests(thread_t * thread)
{
	struct ip_vs_get_dests *d;
	socklen_t len;
    int index;
	int i;


	len = sizeof(*d) + sizeof(struct ip_vs_dest_entry)* global_vs->num_dests;
	if (!(d = malloc(len)))
		return 0;

	d->protocol = IPPROTO_TCP;
	//d->addr = (uint32_t)(global_vs->addr);
	d->port = (uint16_t)(global_vs->port);
	d->num_dests = global_vs->num_dests;

	if (getsockopt(sockfd, IPPROTO_IP, IP_VS_SO_GET_DESTS, d, &len) < 0) {
		free(d);
		log_message(LOG_ERR, "IP_VS_SO_GET_DESTS fail, %s", ipvs_strerror(errno));  
		return 0;
	}


    for(i = 0; i < d->num_dests; i++)
	{
		index = check_ipaddr_exist(d->entrytable[i].addr);
		if(index != -1)
			global_vs->entrytable[index].dest_rate = d->entrytable[i].stats.cps; 	
	}

	return 1;
}


void set_ip_mark(int index, int val)
{
    if(index >= 20){
		return;
	}

	global_vs->entrytable[index].mark = val;
}

int check_ipaddr_exist(int ipaddr)
{
	int i;
	salt_real_server_t *rs ;

	for(i = 0; i < global_vs->num_dests; i++)
	{
	    rs = &global_vs->entrytable[i];
		if(rs->ipaddr == ipaddr)
			return i;
	}

	return -1;
}


void start_salt_stat(void)
{
    //allocate global data structure for statistics
    
	thread_add_timer(master, ipvs_salt_get_dests, NULL, BOOTSTRAP_DELAY);
}


void init_comm_salt(void)
{
	start_comm_salt(NULL);
	start_salt_stat();
}

int ipvs_init(void)
{
	socklen_t len;
	struct ip_vs_getinfo ipvs_info;

	len = sizeof(ipvs_info);
	if ((sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)) == -1)
		return -1;

	if (getsockopt(sockfd, IPPROTO_IP, IP_VS_SO_GET_INFO,
		       (char *)&ipvs_info, &len))
		return -1;

	return 0;
}


int start_comm_salt(thread_t * thread)
{
	struct sockaddr_in srcaddr, dstaddr;  
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
    srcaddr.sin_port        =  htons(35938);
    srcaddr.sin_addr.s_addr =  INADDR_LOOPBACK;

    if(bind(sock_fd,(struct sockaddr *)&srcaddr, sizeof(srcaddr)) == -1)
    {
        close(sock_fd);
        log_message(LOG_ERR, "binding salt error: %s", ipvs_strerror(errno));
        goto thread_add;
    }

	//set nonblock
	flags = fcntl(sock_fd, F_GETFL, 0);
	fcntl(sock_fd, F_SETFL, flags | O_NONBLOCK);

	dstaddr.sin_family		=  AF_INET;
	dstaddr.sin_port		=  htons(35937);
	dstaddr.sin_addr.s_addr =  INADDR_LOOPBACK;
	ret = connect(sock_fd, (struct sockaddr *)&dstaddr, sizeof(dstaddr));

thread_add:
    if(ret < 0)
		thread_add_timer(master, start_comm_salt, NULL, BOOTSTRAP_DELAY);
	else
	{
	    salt_sock_fd = sock_fd;
		thread_add_read(master, lbd_rcvmsg_salt, 0, sock_fd, BOOTSTRAP_DELAY);
	}
	
	return 0;
	
}


