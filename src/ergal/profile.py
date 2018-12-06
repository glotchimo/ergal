""" ergal Profile module. """

import os
import json
import hashlib
import sqlite3
from warnings import warn

from ergal import utils

import xmltodict as xtd
import requests
from requests.exceptions import ConnectionError  
       

class Profile:
    """ Manages API profiles. """
    def __init__(self, name, base=None, test=False):
        """ Initialize Profiler class.

        Profile handles the creation and storage of API profiles.
        These objects are created and stored in a local 
        SQLite database called 'ergal.db'.
        
        Arguments:
            name -- the name of the profile

        Keyword Arguments:
            base -- the API's base URL
            test -- tells the util to create a test database
                    that will be deleted following tests
        
        """
        self.id = (
            hashlib.sha256(
            bytes(name, 'utf-8'))
            .hexdigest()
            [::2][::2])
        
        self.name = name
        self.base = base
        self.auth = {}
        self.endpoints = {}

        self.db, self.cursor = utils.get_db(test)

        try:
            self._get()
        except Exception as e:
            if str(e) == 'get: no matching record':
                self._create()
            else:
                raise Exception('get: selection failed')

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
        sql = """INSERT INTO Profile (id, name, base) VALUES (?, ?, ?)"""
        with self.db:
            self.cursor.execute(sql, (self.id, self.name, self.base,))

        return "Profile for {name} created at {id}.".format(
            name=self.name,
            id=self.id)
    
    def call(self, name, **kwargs):
        """ Call an endpoint.

        Arguments:
            name -- the name of an endpoint
        
        """    
        endpoint = self.endpoints[name]
        url = self.base + endpoint['path']

        for k in kwargs:
            if k in ('headers', 'params', 'data'):
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
            sql = ("UPDATE ProfileSET ? = ? WHERE id = ?")
            with self.db:
                self.cursor.execute(sql, (field[0], field[1], self.id,))

        return "Fields for {name} updated at {id}".format(
            name=self.name,
            id=self.id)

    def set_auth(self, method, **kwargs):
        """ Set authentication details.

        Arguments:
            method -- a supported auth method
        
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

        Arguments:
            name -- a name describing the given endpoint
            path -- the given path to the API endpoint
            method -- the method assigned to the given endpoint

        """
        endpoint = {'path': path,
                    'method': method}

        for key in ('params', 'data', 'headers', 'auth'):
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
        
        Arguments:
            name -- the name of an endpoint.

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