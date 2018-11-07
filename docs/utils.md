# ERGAL Official Documentation
## The Utility Module - `utils.py`

### __`class: Profile(name, base='', test=False)`__
#### Docstring
    Initialize Profiler class.

    Profiler handles the creation and storage of API profiles.
    These objects are created and stored in SQLite database.

    Arguments:
        str:name -- the name of the profile

    Keyword Arguments:
        str:base -- the API's base URL
        bool:test -- 
            tells the class to create a test database
            that will be deleted post-tests
    
    Example:
    >>> new_profile = Profile(
        'Test Profile',
        base='https://api.test.com')
    >>> new_profile.set_auth('key-header', key='tester', name='token')
    >>> new_profile.add_endpoint('tests', path='/tests', method='get')


#### Construction
On `__init__` several things happen:

1. **Argument Validation** - `name` and `base` are confirmed as strings, then `base` is checked as a valid URL. If it is not, `self.base` will be set to an empty string and the following warning will be raised:

        UserWarning: base argument rejected: invalid URL.

2. **Database Setup** - sqlite connects to or creates the `ergal.db` database file, then creates the `Profile` table if it does not exist.

    *Note: if `test` is `True`, sqlite will create a database file called `ergal_test.db`*.

3. **Row Selection/Insertion** - after the database connection and cursor have been set up, `self._get()` is run; if no record is returned, `self._create()` is called to insert the record into the `Profile` table.


### __`Profile` Methods__
#### __`_get(self)`__ Get the record from the Profile table.

Uses the instance's ID value to pull the corresponding record from the database. If no record is found, `ProfileException` is raised, allowing `__init__` to insert the record.

#### __`_create(self)`__ Create a record in the Profile table.

Using only the current instance's id, name, and base, a row is inserted into the Profile table.

#### __`set_auth(self, method, **kwargs)`__ Set authentication details for the API profile.
**Arguments:**

- `str:method` - a str specifying a supported auth method.

**Keyword Arguments:**

- `str:key` - an API key
- `str:name` - a name for the given API key
- `str:username` - an API username
- `str:password` - an API password

Depending the method specified as an argument, keyword arguments are validated and serialized to be stored in the database.

These are the currently supported auth types:

1. `method: basic` - basic username/password authentication. Requires `username` and `password` keyword arguments.
    
    Example:

        >>> profile.set_auth('basic', username='tester', password='password')

2. `method: key-header` - a key passed as an HTTP header. Requires `key` and `name` arguments to specify under what name the key should be passed in the headers.

    Example:

        >>> profile.set_auth('key-header', key='testkey', name='auth-token')

3. `method:key-query` - a key passed in the HTTP query. Requires `key` and `name` arguments to specify how the key should be added to the query.

    Example:

        >>> profile.set_auth('key-query', key='testkey', name='key')

#### __`add_endpoint(self, name, path, method, **kwargs)`__ Add an endpoint to the API profile.
**Arguments:**

- `str:name` - the name identifying the given endpoint
- `str:path` - the path to the desired endpoint, not including the base URL.
- `str:method` - the assigned HTTP method for the given endpoint.

**Keyword Arguments:**

- `bool:auth` - a boolean stating whether authentication is necessary on the given endpoint
- `str:params` - a dict of query parameters to be appended to the request URL.
- `str:data` - a dict to be passed as JSON via update/post/etc.
- `str:headers` - a dict of headers to be passed as HTTP headers.

The `path` and `method` arguments are validated, packaged in a dict, and added to the instance variable `endpoints` which is a list. That list is then serialized and added to the respective row in the database.

All endpoints are scrubbed such that they match the necessary form (/<>). If a bad endpoint is encountered, a warning is raised and the endpoint is corrected before being added to the API profile.

Additional keyword arguments can be used (`params`, `data` and `headers`). These values are not validated, scrubbed or altered, so it is up to the user to ensure that everything is in order according to the API.

Example:

    >>> profile.add_endpoint('get tests', '/tests', 'get')
    >>> profile.add_endpoint('submit test', '/tests/submit', 'post')
    >>> print(profile.endpoints)
    {'get tests': {'path': '/tests', 'method': 'get'}, 'submit test': {'path': '/tasks/submit', 'method': 'post'}}

#### __`del_endpoint(self, name)`__ Delete an endpoint from the API profile.
**Arguments:**

- `str:name` - the name of the endpoint to delete.

If the name matches with an endpoint dict in `self.endpoints`, the endpoint is removed from `self.endpoints` and the field is updated in the respective row in the database.

Example:

    >>> profile.endpoints
    [{'name': 'test', 'path': '/test', 'method': 'get'}]
    >>> profile.del_endpoint('test')
    >>> profile.endpoints
    []