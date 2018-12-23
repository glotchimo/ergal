"""
ergal.utils
~~~~~~~~~~~

This module implements the utility methods used by the
Profile interface.

:copyright: (c) 2018 by Elliott Maguire
"""

import os
import json
import sqlite3
import hashlib

import requests
import xmltodict as xtd


def get_db(test=False):
    """ Get/create a database connection.

    If a local ergal.db file exists, a connection 
    is established and returned, otherwise a new 
    database is created and the connection is returned.

    :param test: (optional) determines whether or not a test database
                            should be created.
    """
    file = 'ergal_test.db' if test else 'ergal.db'
    db = sqlite3.connect(file)
    cursor = db.cursor()

    db.execute("""
        CREATE TABLE IF NOT EXISTS Profile (
            id          TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            base        TEXT    NOT NULL,
            auth        TEXT,
            endpoints   TEXT,

            PRIMARY KEY(id))""")

    return db, cursor


def parse(response, targets=None):
    """ Parse response data.

    :param response: a requests.Response object
    :param targets: (optional) a list of data targets
    """
    try:
        data = json.loads(response.text)
    except:
        data = xtd.parse(response.text)
    
    def search(d):
        for k in d:
            if k in targets:
                return d[k]
            elif type(d[k]) in [dict, list]:
                for i in d[k]:
                    for j in search(i):
                        yield j
    
    output = {i.name: i.value for i in search(data)} if targets else data
    return dict(output)

