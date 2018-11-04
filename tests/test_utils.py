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


class TestUtilites(unittest.TestCase):
    def test_construction_proper(self):
        """ Test construction with proper parameters. """
        profile = utils.Profile(
            'test_api_profile_0',
            base='https://jsonplaceholder.typicode.com',
            test=True)

        profile.add_auth(
            {'auth-type': 'headers', 'token': 'test token'})

        profile.add_endpoint('/users')
        profile.add_endpoint('/posts')

        self.assertIsInstance(profile, utils.Profile)
        self.assertEqual(
            profile.base,
            'https://jsonplaceholder.typicode.com')

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
                base='https://jsonplaceholder.typicode.com',
                test=True)

        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_1',
                base='jsonplaceholder.typicode.com',
                test=True)

        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_2',
                base='https://json placeholder.typicode.com',
                test=True)

        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_3',
                base='https://jsonplaceholder',
                test=True)
        
        with self.assertWarns(UserWarning):
            utils.Profile(
                'test_api_profile_4',
                base='https://jsonplaceholder.typicode.com/',
                test=True)

    def test_construction_database(self):
        """ Test construction database operation. """
        profile = utils.Profile(
            'test_api_profile_5',
            base='https://jsonplaceholder.typicode.com',
            test=True)
        
        profile.add_auth({'token': 'test token'})
        profile.add_endpoint('/users')
        profile.add_endpoint('/posts')

        profile.db.close()

        profile = utils.Profile(
            'test_api_profile_5',
            'https://jsonplaceholder.typico.com',
            test=True)

        self.assertEqual(profile.auth, {'token': 'test token'})
        self.assertEqual(profile.endpoints, ['/users', '/posts'])

        profile.db.close()
        os.remove('ergal_test.db')

