""" Utility tests. """

import os
import unittest

from ergal.profile import Profile


def build_profile():
    profile = Profile(
        'Test API Profile',
        base='https://httpbin.org',
        test=True)
    
    return profile


class TestProfile(unittest.TestCase):
    """ All tests for the profile module and Profile class. """
    def test_init(self):
        profile = build_profile()
        self.assertIsInstance(profile, Profile)

        profile = Profile(1, base=1, test=True)
        self.assertEqual(profile.name, 'default')
        self.assertEqual(profile.base, 'default')

        profile.db.close()
        os.remove('ergal_test.db')

    def test_call(self):
        profile = build_profile()
        profile.add_endpoint('JSON', '/json', 'get')
        profile.add_endpoint('XML', '/xml', 'get')

        self.assertIsInstance(profile.call('JSON'), dict)
        self.assertIsInstance(profile.call('XML'), dict)

        profile.db.close()
        os.remove('ergal_test.db')
    
    def test_set_auth(self):
        profile = build_profile()
        self.assertIsInstance(profile, Profile)

        profile.set_auth('header', name='test', key='test')
        self.assertEqual(profile.auth, {
            'method': 'header',
            'name': 'test',
            'key': 'test'})

        profile.db.close()
        os.remove('ergal_test.db')

    def test_add_endpoint(self):
        profile = build_profile()
        self.assertIsInstance(profile, Profile)

        profile.add_endpoint('Test', '/test', 'get')
        self.assertEqual(profile.endpoints, {
            'Test': {
                'path': '/test',
                'method': 'get'}})
        
        profile.db.close()
        os.remove('ergal_test.db')


if __name__ == "__main__":
    unittest.main()

