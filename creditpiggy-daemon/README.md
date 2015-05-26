
# Creditpiggy Daemon

This folder contains the project-side daemon that is responsible for batching and throttling the requests to the creditpiggy server, minimizing the delays when interfacing with the application batch system.

The daemon is designed to be self-contained and with minimal python requirements in order to be easily deployed in any environment.

## Configuration

In order to use the CreditPiggy daemon you will need to provide the following minimal configuration:

```ApacheConf
[api]

# Project authentication 
project_id=d6db27eb65704bb6acb3b83ceaf95e40
project_auth=561c18dedd604057b9f4852fda842faba5abbc09e7674bc5a4716d3d9d3a236f

[server]

# Use the following config in order to bind on a unix socket (Recommended)
socket=unix
bind=/var/run/creditapi.socket

# Use the following config if you are using a dedicated machine that runs
# the daemon
socket=tcp
bind=0.0.0.0:9999
```

## Interfacing with the daemon

The daemon protocol is very simple and can even be used in bash with just a few lines of code.

The overall format of the command frames is the following:

```
COMMAND[,parameter=value[,...]]
```

For example, you can allocate a job in your scheduler using:

```bash
echo "ALLOC,uuid=job_unique_id" | nc -U /var/run/creditapi.socket
```

### API Reference

The following commands are supported by the CreditPiggy daemon:

<table>

    <tr>
        <th colspan="2">ALLOC</th>
        <td>Allocate a new credit slot for use in your project.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>uuid=</th>
        <td>The unique id of the job. This ID must be unique in your project, but it does not need to be unique in the CreditPiggy system.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>min=</th>
        <td>The minimum number of credits to allocate for this slot.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>max=</th>
        <td>The maximum number of credits to allocate for this slot.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>credits=</th>
        <td>Instead of providing <em>min=</em> and <em>max=</em> you can provide this parameter if you want to give a fixed number of credits to the user upon completing the task.</td>
    </tr>


    <tr>
        <th colspan="2">CLAIM</th>
        <td>Claim credits by tagging a job ID to a machine ID.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>uuid=</th>
        <td>The unique id of the job. This job ID must be allocated first using the ALLOC command.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>machine=</th>
        <td>The UUID of the machine that processed this job.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>credits=</th>
        <td>The amount of credits to give to the machine for completing this job. This parameter is ignored if the designated job slot was allocated with the <em>credits=</em> parameter defined.</td>
    </tr>

    <tr>
        <th colspan="2">COUNTERS</th>
        <td>Increment or decrement specific counters that were produced by this job.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>uuid=</th>
        <td>The unique id of the job. This job ID must be allocated first using the ALLOC command.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>[name]=&plusmn;n</th>
        <td>Any other parameter is considered to be named counter. The value of this counter will be aggregated on the machines and the user profile. This is useful if you want to customise awards and badges.</td>
    </tr>


    <tr>
        <th colspan="2">META</th>
        <td>Specify arbitrary metadata for this job, useful for debugging or award or badge assignment.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>uuid=</th>
        <td>The unique id of the job. This job ID must be allocated first using the ALLOC command.</td>
    </tr>
    <tr>
        <td>&nbsp;</td>
        <th>[name]=</th>
        <td>Any other parameter is considered to be metadata property. These values remain bound with the job and are not aggregated to the user's or machine's profile.</td>
    </tr>

</table>


