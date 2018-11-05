""" ERGAL utilities. """

import os
import json
import hashlib
import sqlite3
from warnings import warn

from ergal.exceptions import HandlerException, ProfileException

import requests


class Handler:
    """ Handles API profiles. """
    def __init__(self, profile):
        """ Initialize the Handler class.

        Handler handles the parsing of API responses according to
        the given API profile.

        Arguments:
            Profile:profile -- an API Profile object.
        
        """
        if not profile:
            raise HandlerException(self, 'init:no profile')

        self.profile = profile

        if self.profile.auth['method'] == 'basic':
            self.auth_method = 'basic'
        elif self.profile.auth['method'] == 'key':
            self.auth_method = 'key'
        else:
            raise HandlerException(profile, 'init: unsupported auth type')
    
    def call(self, endpoint):
        """ Call an endpoint.
        
        """


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
        if base[:8] not in 'https://':
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
        self.endpoints = []

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
        
    def add_auth(self, auth):
        """ Add authentication details.

        Using the current instance's id and auth dict,
        the auth field is updated in the respective row.
        
        """
        if not auth:
            raise ProfileException(self, 'add_auth: no auth')
        elif type(auth) != dict:
            raise ProfileException(self, 'add_auth: invalid auth')
        elif 'method' not in auth:
            warn('auth altered: no method specified')
            if 'username' in auth and 'password' in auth:
                auth['method'] = 'basic'
            elif 'key-headers' in auth and 'name' in auth:
                auth['method'] = 'key-headers'
            elif 'key-query' in auth and 'name' in auth:
                auth['method'] = 'key-query'
            else:
                raise ProfileException(self, 'add_auth: invalid auth')

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
            return "Authentication details for {name} added at {id}".format(
                name=self.name,
                id=self.id)
        
    def add_endpoint(self, endpoint):
        """ Add an endpoint. 
        
        Using the current instance's id and an endpoint
        dict passed as an argument, the given endpoint is added
        to the instance's endpoints list, which is then set
        via an update to the respective record.

        Arguments:
            dict:endpoint -- a dict of endpoint information

        """
        if not endpoint:
            raise ProfileException(self, 'add_endpoint: empty endpoint')
        elif type(endpoint) != dict:
            raise ProfileException(self, 'add_endpoint: invalid endpoint')
        elif 'path' not in endpoint:
            raise ProfileException(self, 'add_endpoint: no path')
        elif 'method' not in endpoint:
            raise ProfileException(self, 'add_endpoint: no method')

        if endpoint['path'][-1] == '/':
            warn('endpoint altered: invalid endpoint')
            endpoint['path'] = endpoint['path'][:-1]
        if endpoint['path'][0] != '/':
            warn('endpoint altered: invalid endpoint')
            endpoint['path'] = '/' + endpoint['path']
        if ' ' in endpoint['path']:
            warn('endpoint altered: invalid endpoint')
            endpoint['path'] = endpoint['path'].replace(' ', '')
        
        self.endpoints.append(endpoint)
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
            return "Endpoints for {name} added at {id}.".format(
                name=self.name,
                id=self.id)

