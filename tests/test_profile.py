""" Utility tests. """

import os
import unittest
import json
import hashlib
import sqlite3

from src.ergal.profile import Profile
from src.ergal.exceptions import ProfileException


def build_profile():
    profile = Profile(
        'Test API Profile',
        base='https://api.test.com',
        test=True)
    
    return profile


class TestProfile(unittest.TestCase):
    def test_construction_proper(self):
        """ Test construction with proper parameters. """
        profile = build_profile()

        profile.set_auth('key-header', key='testkey', name='test')

        profile.add_endpoint('list users', '/users', 'get')
        profile.add_endpoint('get post', '/posts', 'get', params={'target': 1})
        profile.add_endpoint('add post',
            '/posts', 'post', data={'post': 'post'})

        self.assertIsInstance(profile, Profile)
        self.assertEqual(
            profile.base,
            'https://api.test.com')

        self.assertEqual(profile.auth, {
            'method': 'key-header',
            'key': 'testkey',
            'name': 'test'})

        self.assertEqual(profile.endpoints, {
            'list users': {'path': '/users', 'method': 'get'},
            'get post': {
                'path': '/posts', 'method': 'get', 'params': {'target': 1}},
            'add post': {
                'path': '/posts',
                'method': 'post',
                'data': {'post': 'post'}}})

        profile.db.close()
        os.remove('ergal_test.db')

    def test_construction_improper(self):
        """ Test construction with improper parameters. """
        with self.assertRaises(Exception):
            profile = Profile(
                ['Test API Profile'],
                base='https://api.test.com',
                test=True)

        # warn for no https://
        with self.assertWarns(UserWarning):
            profile = Profile(
                'test_api_profile_1',
                base='api.test.com',
                test=True)

        # warn for whitespace
        with self.assertWarns(UserWarning):
            profile = Profile(
                'test_api_profile_2',
                base='https:// api.test.com',
                test=True)

        # warn for no .
        with self.assertWarns(UserWarning):
            profile = Profile(
                'test_api_profile_3',
                base='https://api',
                test=True)
        
        # warn for trailing /
        with self.assertWarns(UserWarning):
            profile = Profile(
                'test_api_profile_4',
                base='https://api.test.com/',
                test=True)

        profile.db.close()
        os.remove('ergal_test.db')

    def test_construction_database(self):
        """ Test construction database operation. """
        profile = build_profile()
        
        profile.set_auth('key-header', key='testkey', name='test')
        profile.add_endpoint('list users', '/users', 'get')
        profile.add_endpoint('get post', '/posts', 'get', params={'target': '1'})
        profile.add_endpoint('add post',
            '/posts', 'post', data={'post': 'post'})

        profile.db.close()

        profile = build_profile()

        self.assertEqual(profile.auth, {
            'method': 'key-header',
            'key': 'testkey',
            'name': 'test'})

        self.assertEqual(profile.endpoints, {
            'list users': {'path': '/users', 'method': 'get'},
            'get post': {
                'path': '/posts', 'method': 'get', 'params': {'target': '1'}},
            'add post': {
                'path': '/posts',
                'method': 'post',
                'data': {'post': 'post'}}})

        profile.db.close()
        os.remove('ergal_test.db')

    def test_set_auth(self):
        """ Test add_auth method. """
        profile = build_profile()

        with self.assertRaises(Exception):
            profile.set_auth(None)
        
        with self.assertRaises(Exception):
            profile.set_auth({})

        with self.assertRaises(Exception):
            profile.set_auth('unsupported method')
        
        with self.assertRaises(Exception):
            profile.set_auth('basic')
        
        with self.assertRaises(Exception):
            profile.set_auth('key-header')

        with self.assertRaises(Exception):
            profile.set_auth('key-query')

        profile.db.close()
        os.remove('ergal_test.db')

    def test_add_endpoint(self):
        """ Test add_endpoint method. """
        profile = build_profile()

        with self.assertRaises(Exception):
            profile.add_endpoint('test', None, 'get')
        
        with self.assertWarns(UserWarning):
            profile.add_endpoint('test', 'test', 'get')
        
        with self.assertWarns(UserWarning):
            profile.add_endpoint('test', path='test/', method='get')
        
        with self.assertWarns(UserWarning):
            profile.add_endpoint('test', path='/ test', method='get')
        
        profile.db.close()
        os.remove('ergal_test.db')
    
    def test_del_endpoint(self):
        """ Test del_endpoint method. """
        profile = build_profile()

        profile.add_endpoint('list users', '/users', 'get')
        self.assertEqual(profile.endpoints, {
            'list users': {'path': '/users', 'method': 'get'}})
        
        profile.del_endpoint('list users')
        self.assertEqual(profile.endpoints, {})

    def test_call(self):
        """ Test caller method. """
        profile = build_profile()
        profile.add_endpoint('get posts', '/posts', 'get')
        profile.add_endpoint('get user post',
            '/posts/user', 'get', params={'userId': 1})

        self.assertIsInstance(profile.call('get posts'), dict)
        self.assertIsInstance(profile.call('get user post'), dict)

        profile.db.close()
        os.remove('ergal_test.db')