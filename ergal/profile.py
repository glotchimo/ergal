"""
ergal.profile
~~~~~~~~~~~~~

This module implements the Profile interface, which enables
the user to manage their API profiles.

:copyright: (c) 2018 by Elliott Maguire
"""

import os
import json
import hashlib
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
    :param test: (optional) dictates whether or not the database
                            instance created should be a test instance.
    """
    def __init__(self, name, base=None, test=False):
        self.name = name if type(name) is str else 'default'
        
        make_id = lambda n: (
            hashlib.sha256(bytes(n, 'utf-8'))
            .hexdigest()[::2][::2])
        self.id = make_id(name) if type(name) is str else 'default'

        self.base = base if type(base) is str else 'default'
        self.auth = {}
        self.endpoints = {}

        self.db, self.cursor = utils.get_db(test)

        try:
            self._get()
        except Exception as e:
            if str(e) == 'get: no matching record':
                self._create()
            else:
                raise Exception('get/create: unknown error occurred')

    def _get(self):
        """ Get an existing profile.. """
        sql = """SELECT * FROM Profile WHERE id = ?"""
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
        
        return "Profile for {name} fetched from {id}.".format(
            name=self.name,
            id=self.id)

    def _create(self):
        """ Create a new profile. """
        sql = "INSERT INTO Profile (id, name, base) VALUES (?, ?, ?)"
        with self.db:
            self.cursor.execute(sql, (self.id, self.name, self.base,))

        return "Profile for {name} created at {id}.".format(
            name=self.name,
            id=self.id)
    
    def call(self, name, **kwargs):
        """ Call an endpoint.

        This method preps request items (url, headers, body),
        then makes a call to the given endpoint. The response is
        then parsed by `utils.parse` to produce an output.

        :param name: the name of the endpoint
        """
        endpoint = self.endpoints[name]
        url = self.base + endpoint['path']

        if 'auth' in endpoint and endpoint['auth']:
            auth = endpoint['auth']
            if auth['method'] == 'header':
                kwargs['headers'][auth['name']] = auth['key']
            elif auth['method'] == 'params':
                kwargs['params'][auth['name']] = auth['key']
            elif auth['method'] == 'basic':
                kwargs['auth'] = (auth['user'], auth['pass'])

        for k in kwargs:
            if k not in ('headers', 'params', 'data'):
                kwargs.pop(k)

        response = getattr(requests, endpoint['method'])(url, **kwargs)

        try:
            data = json.loads(response.text)
        except:
            data = xtd.parse(response.text)
        finally:
            return data
    
    def update(self):
        """ Update the current profile's record. """
        fields = vars(self)
        for field in fields.items():
            sql = "UPDATE Profile SET ? = ? WHERE id = ?"
            with self.db:
                self.cursor.execute(sql, (field[0], field[1], self.id,))

        return "Fields for {name} updated at {id}".format(
            name=self.name,
            id=self.id)

    def set_auth(self, method, **kwargs):
        """ Set authentication details.

        :param method: a supported authentication method
        """
        auth = {'method': method}

        for k, v in kwargs.items():
            if k in ('key', 'name', 'username', 'password'):
                auth[k] = v

        self.auth = auth
        auth_str = json.dumps(self.auth)
        sql = "UPDATE Profile SET auth = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (auth_str, self.id,))
        
        return "Authentication details for {name} set at {id}".format(
            name=self.name,
            id=self.id)
        
    def add_endpoint(self, name, path, method, **kwargs):
        """ Add an endpoint.

        :param name: a name for the endpoint
        :param path: the path, from the base URL, to the endpoint
        :param method: a supported HTTP method
        """
        endpoint = {'path': path,
                    'method': method}

        for key in ('params', 'data', 'headers', 'auth', 'targets'):
            if key in kwargs:
                endpoint[key] = kwargs[key]
            else:
                continue
        
        self.endpoints[name] = endpoint
        endpoints_str = json.dumps(self.endpoints)

        sql = "UPDATE Profile SET endpoints = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (endpoints_str, self.id,))
        
        return "Endpoint {path_name} for {name} added at {id}.".format(
            path_name=name,
            name=self.name,
            id=self.id)

    def del_endpoint(self, name):
        """ Delete an endpoint.

        :param name: the name of an endpoint
        """
        del self.endpoints[name]
        endpoints_str = json.dumps(self.endpoints)

        sql = "UPDATE Profile SET endpoints = ? WHERE id = ?"
        with self.db:
            self.cursor.execute(sql, (endpoints_str, self.id,))

        return "Endpoint {path} for {name} deleted from {id}.".format(
            path=name,
            name=self.name,
            id=self.id)
    
    def add_target(self, endpoint, target):
        """ Add a data target.
        
        :param endpoint: the name of the endpoint
        :param target: the name of the target field
        """

