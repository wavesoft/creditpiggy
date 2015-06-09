
# Python API

The `cpdaemon` library provides all the high-level routines for interfacing with the creditpiggy daemon that runs in the job-manager site.

If your job management mechanism is written in python, you can use this library off the shelf.

## API Reference

The following functions are exposed by the `creditapi` library:

### cpapi_setup(server_endpoint, credentials=None)

Initialises the CreditPiggy api library. This function should be called in order to define the endpoint where the daemon is running.

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Desc</th>
    </tr>
    <tr>
        <th><code>server_endpoint</code></th>
        <th><code>string</code></th>
        <td>
            The daemon endpoint. Depending on the format of the string, three different types of endpoints can be defined:
            <ul>
                <li><code>UNIX Socket</code> (ex. "/var/run/creditapi.socket"): Indicate that the daemon runs locally under the specified UNIX socket.</li>
                <li><code>Network Endpoint</code> (ex. "1.2.3.4:5667"): Indicate that the daemon runs remotely under the specified network endpoint.</li>
                <li><code>URL</code> (ex. "https://cp.org/api"): Indicate that no intermediate daemon should be used, but the library should directly contact the CreditPiggy server under the specified API URL. When you use this option, <code>credentials</code> should contain a tuple with your <code>(project_id, project_auth)</code>. <strong>NOTE: This option is not implemented yet!</strong> </li>
            </ul>
        </td>
    </tr>
</table>

### cpapi_alloc(slot_id, min=None, max=None, credits=None)

Allocate a slot with the specified ID and give the specified credits or credit range on it.

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Desc</th>
    </tr>
    <tr>
        <th><code>slot_id</code></th>
        <th><code>string</code></th>
        <td>
            A unique ID that identifies the slot to allocate. This ID should be unique throughout your project but it doesn't need to be globally unique.
        </td>
    </tr>
    <tr>
        <th><code>min, max</code></th>
        <th><code>integer</code></th>
        <td>
            The minimum and maximum number of credits this slot is capable of
            giving. The exact amount is defined during claim, but cannot be out of the specified bounds.
        </td>
    </tr>
    <tr>
        <th><code>credits</code></th>
        <th><code>integer</code></th>
        <td>
            The exact number of credits this slot will give to the machine that claims it.
        </td>
    </tr>
</table>

### cpapi_discard(slot_id, reason=None)

Discard the slot 'slot_id', optionally indicating the reason for doing so. Such reason might be 'expired', 'invalid', 'lost' etc.
<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Desc</th>
    </tr>
    <tr>
        <th><code>slot_id</code></th>
        <th><code>string</code></th>
        <td>
            A unique ID that identifies the slot to allocate. This ID should be unique throughout your project but it doesn't need to be globally unique.
        </td>
    </tr>
    <tr>
        <th><code>rason</code></th>
        <th><code>string</code></th>
        <td>
            A short identifier that explains the reason why the slot was discarded. Such reasons could be 'expired', 'invalid', 'lost' etc.
        </td>
    </tr>
</table>

### cpapi_claim(slot_id, machine_id, credits=None)

Claim a slot previously allocated with `cpapi_alloc` by the machine with the specified `machine_id`. If credits were not allocated at allocation-time, you can specify the credits to give now. 

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Desc</th>
    </tr>
    <tr>
        <th><code>slot_id</code></th>
        <th><code>string</code></th>
        <td>
            A unique ID that identifies the slot to allocate. This ID should be unique throughout your project but it doesn't need to be globally unique.
        </td>
    </tr>
    <tr>
        <th><code>machine_id</code></th>
        <th><code>string</code></th>
        <td>
            The unique ID of the machine that did the computation. This ID is later translated to a user ID by the CreditPiggy server.
        </td>
    </tr>
    <tr>
        <th><code>credits</code></th>
        <th><code>integer</code></th>
        <td>
            The number of credits to give to the machine. If <code>credits</code> was defined when allocating the slot, this is ignored. If a <code>min,max</code> pair was defined when allocating the slot the value is going to be limited within its bounds.  
        </td>
    </tr>
</table>

### cpapi_counters(slot_id, **kwargs)

Specify one or more counters that will be accumulated to both machine and user's profile upon claiming the slot. 

This can be useful when giving badges or marking other achievements to the users.

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Desc</th>
    </tr>
    <tr>
        <th><code>slot_id</code></th>
        <th><code>string</code></th>
        <td>
            A unique ID that identifies the slot to allocate. This ID should be unique throughout your project but it doesn't need to be globally unique.
        </td>
    </tr>
    <tr>
        <th><code>**kwargs</code></th>
        <th><code>int</code></th>
        <td>
            Any other argument is a named counter, whose value will be accumulated upon claiming.
        </td>
    </tr>
</table>

### cpapi_meta(slot_id, **kwargs)

Specify one or more metadata for the specified slot. These metadata are mapped to the slot itself and are not aggregated to the user's or machine's profile. 

<table>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Desc</th>
    </tr>
    <tr>
        <th><code>slot_id</code></th>
        <th><code>string</code></th>
        <td>
            A unique ID that identifies the slot to allocate. This ID should be unique throughout your project but it doesn't need to be globally unique.
        </td>
    </tr>
    <tr>
        <th><code>**kwargs</code></th>
        <th><code>string</code></th>
        <td>
            Any other argument is a named metadata parameter, whose value will be accumulated upon claiming.
        </td>
    </tr>
</table>
