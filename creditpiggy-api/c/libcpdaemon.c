
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/un.h>

#include "creditapi.h"

/**
 * Specift the CreditPiggy API Endpoing
 */
int cpapi_setup ( const char* server_endpoint )
{
    int s, s2, t, len;
    struct sockaddr_un local, remote;
    char str[100];

    // Try to open a unix socket
    if ((s = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        return 0;
	}
}

/**
 * Allocate a credit slot
 */
int cpapi_alloc ( const char* slot_id, int min, int max, int credits, int expire )
{

}

/**
 * Claim a credit slot
 */
int cpapi_claim ( const char* slot_id, const char* machine_id, int credits )
{

}

/**
 * Discard a credit slot
 */
int cpapi_claim ( const char* slot_id, const char* reason )
{

}

/**
 * Update a credit slot counter
 */
int cpapi_counters ( const char* slot_id, const char* counter, int value )
{

}

/**
 * Update a credit slot metadata
 */
int cpapi_meta ( const char* slot_id, const char* key, const char* value )
{

}
