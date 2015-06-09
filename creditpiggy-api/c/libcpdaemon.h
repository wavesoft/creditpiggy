/**
 * CreditPiggy - A Community Credit Management System
 * Copyright (C) 2013 Ioannis Charalampidis
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

#ifndef _CREDITAPI_H_
#define _CREDITAPI_H_

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Specift the CreditPiggy API Endpoing
 */
int cpapi_setup 	( const char* server_endpoint );

/**
 * Allocate a credit slot
 */
int cpapi_alloc 	( const char* slot_id, int min = 0, int max = 0, int credits = 0, int expire = 0 );

/**
 * Claim a credit slot
 */
int cpapi_claim 	( const char* slot_id, const char* machine_id, int credits = 0 );

/**
 * Discard a credit slot
 */
int cpapi_claim 	( const char* slot_id, const char* reason = NULL );

/**
 * Update a credit slot counter
 */
int cpapi_counters 	( const char* slot_id, const char* counter, int value = 1 );

/**
 * Update a credit slot metadata
 */
int cpapi_meta 		( const char* slot_id, const char* key, const char* value );


#ifdef __cplusplus
}
#endif

#endif

