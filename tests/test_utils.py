""" Utility tests. """

import os
import unittest
import json
import hashlib
import sqlite3

from src.ergal import utils
from src.ergal.exceptions import (
    ProfileException
)

import requests


def build_profile():
    profile = utils.Profile(
        'Test API Profile',
        base='https://api.test.com',
        test=True)
    
    return profile


class TestUtilites(unittest.TestCase):
    def test_construction_proper(self):
        """ Test construction with proper parameters. """
        profile = build_profile()

        profile.add_auth(
            {'auth-type': 'headers', 'token': 'test token'})

        profile.add_endpoint('/users')
        profile.add_endpoint('/posts')

        self.assertIsInstance(profile, utils.Profile)
        self.assertEqual(
            profile.base,
            'https://api.test.com')

        self.assertEqual(
            profile.auth,
            {'auth-type': 'headers', 'token': 'test token'})

        self.assertEqual(
            profile.endpoints,
            ['/users', '/posts'])

        profile.db.close()
        os.remove('ergal_test.db')

    def test_construction_improper(self):
        """ Test construction with improper parameters. """
        with self.assertRaises(Exception):
            utils.Profile(
                ['Test API Profile'],
                base='https://api.test.com',
                test=True)

        # warn for no https://
        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_1',
                base='api.test.com',
                test=True)

        # warn for whitespace
        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_2',
                base='https:// api.test.com',
                test=True)

        # warn for no .
        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_3',
                base='https://api',
                test=True)
        
        # warn for trailing /
        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_4',
                base='https://api.test.com/',
                test=True)

    def test_construction_database(self):
        """ Test construction database operation. """
        profile = build_profile()
        
        profile.add_auth({'token': 'test token'})
        profile.add_endpoint('/users')
        profile.add_endpoint('/posts')

        profile.db.close()

        profile = build_profile()

        self.assertEqual(profile.auth, {'token': 'test token'})
        self.assertEqual(profile.endpoints, ['/users', '/posts'])

        profile.db.close()
        os.remove('ergal_test.db')

    def test_add_auth(self):
        """ Test add_auth method. """
        profile = build_profile()

        with self.assertRaises(Exception):
            profile.add_auth({})
        
        with self.assertRaises(Exception):
            profile.add_auth('not a dict')
        
        profile.db.close()
        os.remove('ergal_test.db')

    def test_add_endpoint(self):
        """ Test add_endpoint method. """
        profile = build_profile()

        with self.assertRaises(Exception):
            profile.add_endpoint('')
        
        with self.assertWarns(UserWarning):
            profile.add_endpoint('test')
        
        with self.assertWarns(UserWarning):
            profile.add_endpoint('test/')
        
        with self.assertWarns(UserWarning):
            profile.add_endpoint('/ test')
        
        profile.db.close()
        os.remove('ergal_test.db')