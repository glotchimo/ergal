""" ERGAL Profile module. """

import os
import json
import hashlib
import sqlite3
from warnings import warn

from ergal.exceptions import HandlerException, ProfileException

import xmltodict as xtd
import requests
from requests.exceptions import ConnectionError  
       

class Profile:
    """ Manages API profiles. """
    def __init__(self, name, base='', test=False):
        """ Initialize Profiler class.

        Profiler handles the creation and storage of API profiles.
        These objects are created and stored in SQLite database.
        
        Arguments:
            str:name -- the name of the profile
        
        Keyword Arguments:
            str:base -- the API's base URL
            bool:test -- 
                tells the class to create a test database
                that will be deleted post-tests
        
        """
        # check args
        if type(name) != str:
            raise ProfileException(self, 'init: invalid name')
        elif type(base) != str:
            raise ProfileException(self, 'init: invalid base')

        # validate base
        if base[:4] != 'http' and '://' not in base:
            warn('base argument rejected: invalid URL.')
            base = ''
        elif ' ' in base or '.' not in base:
            warn('base argument rejected: invalid URL.')
            base = ''
        elif base[-1:] == '/':
            warn('base argument altered: trailing /')
            base = base[:-1]

        self.id = hashlib.sha256(bytes(name, 'utf-8')).hexdigest()[::2]
        self.name = name
        self.base = base
        self.auth = {}
        self.endpoints = {}

        # create db/table if nonexistent
        if not test:
            self.db = sqlite3.connect('ergal.db')
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS Profile (
                    id          TEXT    NOT NULL,
                    name        TEXT    NOT NULL,
                    base        TEXT    NOT NULL,
                    auth        TEXT,
                    endpoints   TEXT,

                    PRIMARY KEY(id)
                )
            """)
            self.cursor = self.db.cursor()
        else:
            self.db = sqlite3.connect('ergal_test.db')
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS Profile (
                    id          TEXT    NOT NULL,
                    name        TEXT    NOT NULL,
                    base        TEXT    NOT NULL,
                    auth        TEXT,
                    endpoints   TEXT,

                    PRIMARY KEY(id)
                )
            """)
            self.cursor = self.db.cursor()

        # create record if nonexistent in database
        try:
            self._get()
        except ProfileException as e:
            if str(e) == 'get: no matching record':
                self._create()
            else:
                raise ProfileException(self, 'get: selection failed')

    def call(self, name, **kwargs):
        """ Call an endpoint.

        The name of an endpoint as set by the user is used to grab
        and endpoint dict that is then used to dictate calls/parsing.
        The response is parsed into a dict and returned.

        Arguments:
            str:name -- 
                a str representing the name of a stored endpoint dict

        Returns:
        
        """
        if type(name) != str:
            return HandlerException(self, 'init: invalid endpoint')
        elif name not in self.endpoints:
            return HandlerException(self, 'init: endpoint does not exist')
        
        endpoint = self.endpoints[name]
        url = self.base + endpoint['path']

        request_kwargs = {}
        for key in ('params', 'data', 'headers'):
            if key in endpoint:
                request_kwargs[key] = endpoint[key]
            elif key in kwargs:
                request_kwargs[key] = kwargs[key]
        
        if endpoint['auth'] and self.auth['method'] == 'key-header':
            if 'headers' in request_kwargs:
                request_kwargs['headers'][self.auth['name']] = self.auth['key']
            else:
                request_kwargs['headers'] = {
                    self.auth['name']: self.auth['key']}
        elif endpoint['auth'] and self.auth['method'] == 'key-query':
            if 'params' in request_kwargs:
                request_kwargs['params'][self.auth['name']] = self.auth['key']
            else:
                request_kwargs['headers'] = {
                    self.auth['name']: self.auth['key']}
        elif endpoint['auth'] and self.auth['method'] == 'basic-header':
            if 'headers' in request_kwargs:
                request_kwargs['headers']['username'] = self.auth['username']
                request_kwargs['headers']['password'] = self.auth['password']
            else:
                request_kwargs['headers'] = {
                    'username': self.auth['username'],
                    'password': self.auth['password']}
        elif endpoint['auth'] and self.auth['method'] == 'basic-params':
            if 'params' in request_kwargs:
                request_kwargs['params']['username'] = self.auth['username']
                request_kwargs['params']['password'] = self.auth['password']
            else:
                request_kwargs['params'] = {
                    'username': self.auth['username'],
                    'password': self.auth['password']}

        try:
            response = getattr(requests, endpoint['method'])(url, **request_kwargs)
        except ConnectionError:
            raise HandlerException(self, 'call: connection refused')
        except:
            raise HandlerException(self, 'call: request failed')

        try:
            data = json.loads(response.text)
        except:
            try:
                data = xtd.parse(response.text)
            except:
                raise HandlerException(self, 'call: parse failed')
            else:
                return dict(data)
        else:
            return data

    def _get(self):
        """ Get the record from the Profile table.

        Uses the instance's ID value to pull the corresponding
        record from the database file. If no record is found, 
        ProfileException is raised, allowing __init__ to insert the record.
        
        """
        if not self.id:
            raise ProfileException(self, 'get: insufficient info')

        sql = """
            SELECT *
            FROM Profile
            WHERE id = ?
        """
        try:
            self.cursor.execute(sql, (self.id,))
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'get: selection failed')
        else:
            record = self.cursor.fetchone()
            if record:
                self.id = record[0]
                self.name = record[1]
                self.base = record[2]
                if record[3]:
                    self.auth = json.loads(record[3])
                else:
                    self.auth = ''
                if record[4]:
                    self.endpoints = json.loads(record[4])
                else:
                    self.endpoints = ''
            else:
                raise ProfileException(self, 'get: no matching record')

    def _create(self):
        """ Create a record in the Profile table.

        Using only the current instance's id, name, and base,
        a row is inserted into the Profile table.
        
        """
        if not self.id or not self.name:
            raise ProfileException(self, 'create: insufficient info')

        sql = """
            INSERT INTO Profile
            (id, name, base)
            VALUES (?, ?, ?)
        """
        try:
            with self.db:
                self.cursor.execute(sql, (self.id, self.name, self.base,))
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'create: insertion failed')
        else:
            return "Profile for {name} created at {id}.".format(
                name=self.name,
                id=self.id)
        
    def set_auth(self, method, **kwargs):
        """ Set authentication details.

        Using the current instance's id and auth dict,
        the auth field is updated in the respective row.

        Arguments:
            str:method -- a supported auth method

        Keyword Arguments:
            str:key -- an authentication key
            str:name -- a name for the given key
            str:username -- a username
            str:password -- a password
        
        """
        if not method:
            raise ProfileException(self, 'add_auth: null method')
        elif type(method) != str:
            raise ProfileException(self, 'add_auth: invalid method type')
        
        if method == 'basic':
            try:
                auth = {
                    'method': method,
                    'username': kwargs['username'],
                    'password': kwargs['password']}
            except:
                raise ProfileException(self, 'add_auth: missing params')
        elif method == 'key-header':
            try:
                auth = {
                    'method': method,
                    'key': kwargs['key'],
                    'name': kwargs['name']}
            except:
                raise ProfileException(self, 'add_auth: missing params')
        elif method == 'key-query':
            try:
                auth = {
                    'method': method,
                    'key': kwargs['key'],
                    'name': kwargs['name']}
            except:
                raise ProfileException(self, 'add_auth: missing params')
        else:
            raise ProfileException(self, 'add_auth: unsupported')

        self.auth = auth
        auth_str = json.dumps(self.auth)
        sql = """
            UPDATE Profile
            SET auth = ?
            WHERE id = ?
        """
        try:
            with self.db:
                self.cursor.execute(sql, (auth_str, self.id,))
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'add_auth: update failed')
        else:
            return "Authentication details for {name} set at {id}".format(
                name=self.name,
                id=self.id)
        
    def add_endpoint(self, name, path, method, **kwargs):
        """ Add an endpoint. 
        
        Using the current instance's id and an endpoint
        dict passed as an argument, the given endpoint is added
        to the instance's endpoints list, which is then set
        via an update to the respective record.

        Arguments:
            str:name -- a name describing the given endpoint

        Keyword Arguments:
            str:path -- the given path to the API endpoint
            str:method -- the method assigned to the given endpoint
            
            str:params -- 
                a dict of query parameters to be added to 
                the end of the request url
            str:data -- a dict to be submitted as JSON via update/post/etc
            str:headers -- a dict to be added to the headers of the request

        """
        if not name or not path or not method:
            raise ProfileException(self, 'add_endpoint: incomplete args')
        elif type(name) != str:
            raise ProfileException(self, 'add_endpoint: invalid input')
        elif type(path) != str:
            raise ProfileException(self, 'add_endpoint: invalid path')
        elif type(method) != str:
            raise ProfileException(self, 'add_endpoint: invalid method input')
        elif method not in ('get', 'post', 'put', 'patch', 'delete'):
            raise ProfileException(self, 'add_endpoint: invalid method type')

        if path[-1] == '/':
            warn('endpoint altered: trailing /')
            path = path[:-1]
        if path[0] != '/':
            warn('endpoint altered: absent root /')
            path = '/' + path
        if ' ' in path:
            warn('endpoint altered: whitespace present')
            path = path.replace(' ', '')

        endpoint = {
            'path': path,
            'method': method}

        for key in ('params', 'data', 'headers', 'auth'):
            if key in kwargs:
                endpoint[key] = kwargs[key]
            else:
                continue
        
        self.endpoints[name] = endpoint
        endpoints_str = json.dumps(self.endpoints)
        sql = """
            UPDATE Profile
            SET endpoints = ?
            WHERE id = ?
        """
        try:
            with self.db:
                self.cursor.execute(sql, (endpoints_str, self.id,))
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'add_endpoint: update failed')
        else:
            return "Endpoint {path_name} for {name} added at {id}.".format(
                path_name=name,
                name=self.name,
                id=self.id)

    def del_endpoint(self, name):
        """ Delete a specified endpoint.
        
        Provided the name of the given endpoint, the dict will
        be removed from from the endpoints list and respective
        row in the database.

        Arguments:
            str:name -- the name of an endpoint.

        """
        if not name or name not in self.endpoints:
            raise ProfileException(self, 'del_endpoint: endpoint does not exist')
        
        del self.endpoints[name]
        endpoints_str = json.dumps(self.endpoints)
        sql = """
            UPDATE Profile
            SET endpoints = ?
            WHERE id = ?
        """
        try:
            with self.db:
                self.cursor.execute(sql, (endpoints_str, self.id,))
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'add_endpoint: update failed')
        else:
            return "Endpoint {path} for {name} deleted from {id}.".format(
                path=name,
                name=self.name,
                id=self.id)