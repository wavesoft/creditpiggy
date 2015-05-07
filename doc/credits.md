
# Credit Allocation

Credits can be given to uses using from two different points:

  1. Credits given by the server
  2. Credits allocated by the server and claimed by the clients

The first mechanism is more secure and more flexible, but might require modifications in the 


## Credits given by the server

Credits can be given by the server using the following endpoint:

    /api/<project>/credit.give

Which accepts the following GET parametrs:

  * __authKey__ : Project authorization key.
  * __authHash__ : Authorization validation checksum.
  * __user__ : The userID to which you want to give credit.
  * __credit__ : The ammount of credit to give.

This query returns a JSON response with the following fields:

  * __result__ : 'ok' if successfuly completed, or 'error' otherwise.
  * [__error__] : The description of the error occured.

## Server allocation / Client consumpsion

Credits can be allocated by the server and bound to a particular job ID using the following endpoint:

    /api/<project>/credit.alloc

Which accepts the following GET parametrs:

  * __authKey__ : Project authorization key.
  * __authHash__ : Authorization validation checksum.
  * __jobid__ : The jobID to link with this credit allocation.
  * __credit__ : The ammount of credit to give when the job is completed.
  * [__useTicket__] : Set to '1' if you want to use enhanced validation of the credit allocation using tickets.

This query returns a JSON response with the following fields:

  * __result__ : 'ok' if successfuly completed, or 'error' otherwise.
  * [__ticket__] : The ticket string if 'useTicket' is specified.
  * [__error__] : The description of the error occured.

Credits can be claimed by the user using the following endpoint:

    /api/<project>/credit.claim

  * __jobid__ : The job ID for which to claim credit from.
  * __user__ : The userID to which you want to give credit.
  * [__ticket__] : If specified, the additional ticket for granting the credits to the user.

