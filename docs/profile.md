Eragl - Official Documentation
==============================

*class* Profile(name, base=None, logs=False, test=False)
--------------------------------------------

The `Profile` class is the core of the Ergal library. It enables the user to create, manage, and access their APIs in a clean manner.

To make a Profile, you need to provide two arguments on initialization, a `name` for the Profile, and a `base` URL.

    >>> from ergal import Profile
    >>> profile = Profile('My API', base='https://my.api')
    Profile for 'My API' created on 4981f61b3b1550ecac46f5f734b9fd68.

A few significant things happen on initialization.

1. Unique ID generation
    - A named UUID5 hash is generated to serve as the `Profile`'s `id` and primary key in the database.

2. Database Initialization
    - A SQLite database file called `ergal.db` is either generated and formatted or connected to by the `utils.get_db` method.

3. Table Initialization
    - If the `Profile` already exists in the database, the `Profile._get` method attempts to retrieve it, but if not, the `Profile._create` method creates a new row with the newly specified information.

*Note: you can specify whether or not `ergal` should print log strings with the `logs` keyword argument on initialization.*

### *async def* call(endpoint, **kwargs)

To call an endpoint, use `Profile.call`, which prepares and issues a request to the URL listen on the endpoint, with the existing or provided options.

    >>> asyncio.run(profile.call('My Endpoint'))
    <Response [200]>

The following call-specific keyword arguments may be supplied:

- `headers`: HTTP header pairs, supplied in a dict format.
- `params`: query parameters, supplied in a dict format.
- `data`: form data, supplied in a dict format.
- `body`: request body, supplied in a str format.

- `pathvars`: a dict of named path variables.

If the `parse` property is specified as `True` on the given endpoint, ergal will parse the response data accordingly (i.e. it will deserialize it if no targets are present, or return target values if they are).

### *async def* add_auth(method, **kwargs)

To add an authentication method to an endpoint, use `Profile.add_auth`, which adds the dict of values to the `Profile.auth` dict and updates it in the database. An approved authentication `method` must be passed as an argument, and the respective keyword arguments must be passed with it.

    >>> asyncio.run(profile.add_auth('headers', name='Authorization', value='Bearer mytoken'))
    Authentication details for 'My API' added on 4981f61b3b1550ecac46f5f734b9fd68.

The following keyword arguments must be supplied in their corresponding contexts:

- **basic**
    - `username`: a username.
    - `password`: a password.
- **headers**
    - `name`: the name of the header pair.
    - `value`: the value to be passed.
- **params**
    - `name`: the name of the query pair.
    - `value`: the value to be passed.
- **digest**
    - `username`: a username.
    - `password`: a password.

Example:

    >>> asyncio.run(profile.add_auth('digest', username='user', password='pass'))
    or
    >>> asyncio.run(profile.add_auth('headers', name='Authorization', value='Bearer myToken123'))

In order to apply an authentication method to an endpoint, the endpoint must have the `auth` property specified as `True`.

### *async def* add_endpoint(name, path, method, **kwargs)

To add an endpoint to an API profile, use `Profile.add_endpoint`, which adds the dict of values to the `Profile.endpoints` dict and updates it in the database. `name`, `path`, and `method` arguments must be passed.

    >>> asyncio.run(profile.add_endpoint('My Endpoint', '/endpoint', 'GET'))
    Endpoint 'My Endpoint' for 'My API' added on 4981f61b3b1550ecac46f5f734b9fd68.

The following endpoint-specific keyword arguments may be supplied:

- `headers`: HTTP header pairs, supplied in a dict format.
- `params`: query parameters, supplied in a dict format.
- `data`: form data, supplied in a dict format.
- `body`: request body, supplied in a str format.

- `auth`: a bool specifying whether or not authentication is required on the endpoint.
- `parse`: a bool specifying whether or not to deserialize/parse response data.
- `targets`: a list of key names of data targets.

#### *async def* del_endpoint(name)

To delete an endpoint, use `Profile.del_endpoint`, which removes it from the `endpoints` dict on the Profile and then updates the JSON object in the database. The `name` of an endpoint must be supplied.

### *async def* add_target(endpoint, target)

To add a data target to an endpoint, use `Profile.add_target`, which adds a str value to the `targets` list on a given `endpoint` and updates it in the database. The `endpoint` name must be supplied as well as the name of the data target.

    >>> asyncio.run(profile.add_target('My Endpoint', 'My Target'))
    Target 'My Target' for 'My Endpoint' added on 4981f61b3b1550ecac46f5f734b9fd68.

#### *async def* del_target(endpoint, target)

To delete a data target, use `Profile.del_target`, which removes the target from the `endpoint`'s `targets` list and updates it in the database. The `endpoint` name must be supplied as well as the name of the data target.