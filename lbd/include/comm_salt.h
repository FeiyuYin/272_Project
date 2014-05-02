
#ifndef _COMM_SALT_H
#define _COMM_SALT_H


typedef enum _salt_msg_type{
        SALT_CONFIG_IPADDR, //0: salt send ip address to lbd,
        SALT_REQUEST_IPADDR, //1: lbd request ip address from salt,
        SALT_IS_MASTER,  //2: lbd notify current node is master
        SALT_IS_SLAVE,   //3: lbd notify current node is slave
        SALT_DISPATCHING_STATS,  //lbd send statistics of dispatching table
        SALT_REQUEST_STATS,  //salt request lbd to send statistics
        SALT_UPGRADE_WEBAPP,  //first phase: tell lbd which node is going to upgrade
        SALT_UPGRADE_CONTINUE, // second phase to upgrade
        SALT_UPGRADE_DONE,
}salt_msg_type_t;

typedef struct _salt_ip_node {
        int ipaddr;
        int port;
        int dispathing_rate;
} salt_ip_node_t;

typedef struct _salt_node_list{
        int type;
        int node_num;
        salt_ip_node_t  entry[0];
}salt_node_list_t;



#endif

