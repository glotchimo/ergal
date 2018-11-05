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
    >>> new_profile.add_auth({'token}: 'test_token'})
    >>> new_profile.add_endpoint('/posts')


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

#### __`add_auth(self, auth)`__ Add authentication details to the API profile.
**Arguments:**

- `dict:auth` - a dict populated with authentication definitions.

The `auth` dict is set to the instance variable `auth` and serialized into JSON and stored in the respective row in the database.

Example:
    
    >>> auth = {
        'method': 'headers',
        'token': 'test_token'}
    >>> profile.add_auth(auth)

#### __`add_endpoint(self, endpoint)`__ Add an endpoint to the API profile.
**Arguments:**

- `str:endpoint` - a str, beginning with a '/', representing an endpoint of the base

The `endpoint` input is added to the instance variable `endpoints` which is a list. That list is then serialized and added to the respective row in the database.

All endpoints are scrubbed such that they match the necessary form (/<>). If a bad endpoint is encountered, a warning is raised and the endpoint is corrected before being added to the API profile.

Example:

    >>> endpoint = '/posts'
    >>> profile.add_endpoint(endpoint)

