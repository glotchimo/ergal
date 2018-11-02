""" ERGAL utilities. """

import os
import json
import hashlib
import sqlite3

from ergal.exceptions import ProfileException

import requests


class Handler:
    """ Handles API profiles. """


class Profile:
    """ Manages API profiles. """
    def __init__(self, name, base=''):
        """ Initialize Profiler class.

        Profiler handles the creation and storage of API profiles.
        These objects are created and stored in SQLite database.
        
        Arguments:
            str:name -- the name of the profile

        Keyword Arguments:
            str:base -- the API's base URL
            dict:auth -- the API's authentication details
            list:endpoints -- a list of endpoints to be accessed.
                              each endpoint is a dict with path, target info, etc.
        
        """
        self.id = hashlib.sha256(
           bytes(name, 'utf-8')
        ).hexdigest()[::2]
        self.name = name
        self.base = base

        self.auth = {}
        self.endpoints = []

        # database operations
        self.db = sqlite3.connect('ergal.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Profile (
                id          INTEGER     NOT NULL
                name        TEXT        NOT NULL
                base        TEXT        NOT NULL
                auth        TEXT        NULL
                endpoints   TEXT        NULL
            )
        """)

    def create_profile(self):
        """ Create a row in the Profile table.

        Using only the current instance's id, namen and base,
        a row is inserted into the Profile table.
        
        """
        if not self.id or not self.name or not self.base:
            raise ProfileException(self, 'create_profile:insufficient info')

        sql = """
            INSERT INTO Profile
            (id, name, base)
            VALUES (
                {id},
                {name},
                {base}
            )
        """.format(
            id=self.id,
            name=self.name,
            base=self.base
        )
        try:
            self.cursor.execute(sql)
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'create_profile:insertion failed')

        return "Profile for {name} created at {id}.".format(
            name=self.name,
            id=self.id
        )
        
    def add_auth(self):
        """ Add authentication details.

        Using the current instance's id and auth dict,
        the auth field is updated in the respective row.
        
        """
        if not self.auth:
            raise ProfileException(self, 'add_auth:no auth values')

        auth_str = json.dumps(self.auth)
        sql = """
            UPDATE Profile
            SET auth = {auth}
            WHERE id = {id}
        """.format(
            id=self.id,
            auth=auth_str
        )
        try:
            self.cursor.execute(sql)
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'add_auth:update failed')

        return "Authentication details for {name} added at {id}".format(
            name=self.name,
            id=self.id
        )
        
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
            raise ProfileException(self, 'add_endpoint:empty endpoint dict')
        
        self.endpoints.append(endpoint)
        endpoints_str = json.dumps(self.endpoints)
        sql = """
            UPDATE Profile
            SET endpoints = {endpoints}
            WHERE id = {id}
        """.format(
            endpoints=endpoints_str,
            id=self.id
        )
        try:
            self.cursor.execute(sql)
        except sqlite3.DatabaseError:
            raise ProfileException(self, 'add_endpoint:update failed')

        return "Endpoints for {name} added at {id}.".format(
            name=self.name,
            id=self.id
        )

