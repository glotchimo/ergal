""" ergal utilities. """

import os
import json
import sqlite3
import hashlib

import xmltodict as xtd
import requests


def get_db(test=False):
    """ Get/create a database connection.

    If a local ergal.db file exists, a connection 
    is established and returned, otherwise a new 
    database is created and the connection is returned.

    Arguments:
        name -- a str name of a database

    Keyword Arguments:
        test -- a bool defining whether or not to
                run for a test config 

    Returns:
        db -- a database connection
        cursor -- a database cursor  
    
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




