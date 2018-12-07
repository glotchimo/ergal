""" Utility tests. """

import unittest

from src.ergal.profile import Profile


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

        profile = Profile(1, base=1)
        self.assertEqual(profile.name, 'default')
        self.assertEqual(profile.base, 'default')

    def test_call(self):
        profile = build_profile()
        profile.add_endpoint('JSON', '/json', 'get')
        profile.add_endpoint('XML', '/xml', 'get')

        self.assertIs(profile.call('JSON'), dict)
        self.assertIs(profile.call('XML'), dict)

        profile.set_auth()

