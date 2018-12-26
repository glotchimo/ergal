# ergal Official Documentation
## The Profile Module - `profile.py`

### __`class: Profile(name, base='', test=False)`__

#### Construction

- **Database Setup** - sqlite connects to or creates the `ergal.db` database file, then creates the `Profile` table if it does not exist.

    *Note: if `test` is `True`, sqlite will create a database file called `ergal_test.db`*.

- **Record Selection/Insertion** - after the database connection and cursor have been set up, `self._get()` is run; if no record is returned, `self._create()` is called to insert the record into the `Profile` table.


### __Methods__
#### __`call(self, name, **kwargs)`__ Call a given endpoint by name.

`str:name` - the name of the endpoint to call.

If the name given matches an existing endpoint on the API profile, that endpoint is called based on its properties, and a `dict` of the response is returned, so long as the response is in JSON or XML format.

Keyword arguments can be used to override or supplement arguments hardcoded to the given endpoint. The accepted keyword arguments correspond with the given method in the `requests` library.

If data targets are supplied, a list of the targetted data will be returned, but not the entire response.

JSON is parsed into a `dict` and XML is parsed into an `OrderedDict`.

Usage:

    >>> profile.call(<endpoint name>)

#### __`_get(self)`__ Get the record from the Profile table.
Uses the instance's ID value to pull the corresponding record from the database. If no record is found, `ProfileException` is raised, allowing `__init__` to insert the record.

#### __`_create(self)`__ Create a record in the Profile table.
Using only the current instance's id, name, and base, a row is inserted into the Profile table.

#### __`set_auth(self, method, **kwargs)`__ Set authentication details for the API profile.

`str:method` - a supported auth method.

Depending the method specified as an argument, keyword arguments are validated and serialized to be stored in the database.

These are the currently supported auth types:

1. `basic` - basic username/password authentication. Requires `username` and `password` keyword arguments.

        >>> profile.set_auth('basic', username=<username>', password=<password>)

2. `header` - a key passed as an HTTP header. Requires `key` and `name` arguments to specify under what name the key should be passed in the headers.

        >>> profile.set_auth('header', key=<key>, name=<name>)

3. `params` - a key passed in the HTTP query. Requires `key` and `name` arguments to specify how the key should be added to the query.

        >>> profile.set_auth('params', key=<key>, name=<name>)

#### __`add_endpoint(self, name, path, method, **kwargs)`__ Add an endpoint to the API profile.

`str:name` - the name identifying the given endpoint

`str:path` - the path to the desired endpoint, not including the base URL.

`str:method` - the assigned HTTP method for the given endpoint.

Arguments are packaged into a dict, then added to the instance variable `endpoints` which is a list. That list is then serialized and added to the respective index in the database.

Additional keyword arguments can be used (`params`, `data`, `headers`, `auth`, and `targets`). These are used to override or supplement call arguments.

Usage:

    >>> profile.add_endpoint(<name>, <path>, <method>)

#### __`del_endpoint(self, name)`__ Delete an endpoint from the API profile.

`str:name` - the name of the endpoint to delete.

If the name matches with an endpoint dict in `self.endpoints`, the endpoint is removed from `self.endpoints` and the field is updated in the respective index in the database.

Usage:

    >>> profile.del_endpoint('')

#### __`add_target(self, endpoint, target)`__ Add a data target to the given endpoint.

`str:endpoint` - the endpoint for the data target to be added to

`str:target` - the key name of the target

After calling the endpoint, the response data is passed through the `parse` utility that, if provided target values, will search through the response and return a list of those targets, in the order they appear in the response.

`add_target` appends the supplied target to the `targets` list on the endpoint, but a list of targets can be specified at call.

Usage:

    >>> profile.call(<endpoint>, targets=[<target>, <target>])