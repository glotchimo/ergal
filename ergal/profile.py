"""
ergal.profile
~~~~~~~~~~~~~

This module implements the Profile interface, which enables
the user to manage their API profiles.
"""

import json
import uuid
import sqlite3

from . import utils

import requests
import xmltodict as xtd


class Profile:
    """ Enables API profile management.

    This class handles the creation/storage/management of API
    profiles in a local SQLite3 database called `ergal.db`, unless
    it is instantiated as a test instance, in which case the
    database is called `ergal_test.db`.

    :param name: a name for the API profile
    :param base: (optional) the base URL of the API
    :param logs: (optional) specifies whether or not log strings
                            are printed on execution of certain methods.
    :param test: (optional) specifies whether or not the database
                            instance created should be a test instance.

    Example:

        >>> profile = Profile('HTTPBin', base='https://httpbin.com')
        >>> profile.add_endpoint('JSON', '/json', 'get')
        >>> profile.call('JSON')
        <dict of response data>
    """
    def __init__(self, name, base=None, logs=False, test=False):
        self.logs = logs

        self.name = name if type(name) is str else 'default'
        self.id = (
            uuid.uuid5(uuid.NAMESPACE_DNS, self.name).hex
            if type(name) is str else 'default')

        self.base = base if type(base) is str else 'default'
        self.auth = {}
        self.endpoints = {}

        self.db, self.cursor = utils.get_db(test=test)

        try:
            self._get()
        except Exception as e:
            if str(e) == 'get: no matching record':
                self._create()
            else:
                raise Exception('get/create: unknown error occurred')

    def _get(self):
        """ Get an existing profile.. """
        sql = "SELECT * FROM Profile WHERE id = ?"
        self.cursor.execute(sql, (self.id,))

        record = self.cursor.fetchone()
        if record:
            self.id = record[0]
            self.name = record[1]
            self.base = record[2]
            self.auth = json.loads(record[3]) if record[3] else {}
            self.endpoints = json.loads(record[4]) if record[4] else {}
        else:
            raise Exception('get: no matching record')

        if self.logs:
            print(f"Profile for {self.name} fetched from {self.id}.")

    def _create(self):
        """ Create a new profile. """
        sql = "INSERT INTO Profile (id, name, base) VALUES (?, ?, ?)"
        with self.db:
            self.cursor.execute(sql, (self.id, self.name, self.base,))

        if self.logs:
            print(f"Profile for {self.name} created on {self.id}.")

    def update(self):
        """ Update a profile's database entry. """
        sql = """
            UPDATE      Profile
            SET         base = ?,
                        auth = ?,
                        endpoints = ?
            WHERE       id = ?"""
        with self.db:
            self.cursor.execute(
                sql, (
                    self.base,
                    json.dumps(self.auth),
                    json.dumps(self.endpoints),
                    self.id))

        if self.logs:
            print(f"Profile for {self.name} updated on {self.id}.")

    async def call(self, name, **kwargs):
        """ Call an endpoint.

        :param name: the name of the endpoint
        """
        endpoint = self.endpoints[name]
        url = self.base + endpoint['path']
        targets = endpoint['targets'] if 'targets' in endpoint else None

        if 'pathvars' in kwargs:
            url = url.format(**kwargs['pathvars'])

        if 'auth' in endpoint and endpoint['auth']:
            if self.auth['method'] == 'headers':
                kwargs['headers'] = {}
                kwargs['headers'][self.auth['name']] = self.auth['value']
            elif self.auth['method'] == 'params':
                kwargs['params'] = {}
                kwargs['params'][self.auth['name']] = self.auth['value']
            elif self.auth['method'] == 'basic':
                kwargs['auth'] = (self.auth['user'], self.auth['pass'])

        for k in list(kwargs):
            if k not in ('headers', 'params', 'data', 'body'):
                kwargs.pop(k)

        response = getattr(requests, endpoint['method'].lower())(url, **kwargs)

        if 'parse' in endpoint and endpoint['parse']:
            data = await utils.parse(response, targets=targets)
            return data
        else:
            return response

    async def add_auth(self, method, **kwargs):
        """ Add authentication details.

        :param method: a supported authentication method
        """
        auth = {'method': method}

        for k, v in kwargs.items():
            if k in ('name', 'value', 'username', 'password'):
                auth[k] = v

        self.auth = auth
        auth_str = json.dumps(self.auth)
        sql = "UPDATE Profile SET auth = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (auth_str, self.id,))

        if self.logs:
            print(f"Authentication details for {self.name} added on {self.id}.")

    async def add_endpoint(self, name, path, method, **kwargs):
        """ Add an endpoint.

        :param name: a name for the endpoint
        :param path: the path, from the base URL, to the endpoint
        :param method: a supported HTTP method
        """
        endpoint = {'path': path,
                    'method': method}

        for key in kwargs:
            if key in (
                'headers', 'params', 'data', 'body',
                'auth', 'parse', 'targets'):

                endpoint[key] = kwargs[key]

        self.endpoints[name] = endpoint
        endpoints_str = json.dumps(self.endpoints)

        sql = "UPDATE Profile SET endpoints = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (endpoints_str, self.id,))

        if self.logs:
            print(f"Endpoint {name} for {self.name} added on {self.id}.")

    async def del_endpoint(self, name):
        """ Delete an endpoint.

        :param name: the name of an endpoint
        """
        del self.endpoints[name]
        endpoints_str = json.dumps(self.endpoints)

        sql = "UPDATE Profile SET endpoints = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (endpoints_str, self.id,))

        if self.logs:
            print(f"Endpoint {name} for {self.name} deleted from {self.id}.")

    async def add_target(self, endpoint, target):
        """ Add a data target.

        :param endpoint: the name of the endpoint
        :param target: the name of the target field
        """
        targets = (
            self.endpoints[endpoint]['targets']
            if 'targets' in self.endpoints[endpoint]
            else [])

        targets.append(target)
        self.endpoints[endpoint]['targets'] = targets
        endpoints_str = json.dumps(self.endpoints)

        sql = "UPDATE Profile SET endpoints = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (endpoints_str, self.id,))

        if self.logs:
            print(f"Target {target} for {endpoint} added on {self.id}.")

    async def del_target(self, endpoint, target):
        """ Delete a data target.

        :param endpoint: the name of the endpoint
        :param target: the name of the target field
        """
        targets = self.endpoints[endpoint]['targets']
        del targets[targets.index(target)]

        self.endpoints[endpoint]['targets'] = targets
        endpoints_str = json.dumps(self.endpoints)

        sql = "UPDATE Profile SET endpoints = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (endpoints_str, self.id,))

        if self.logs:
            print(f"Target {target} for {endpoint} deleted from {self.id}.")

