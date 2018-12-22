""" Utility tests. """

import os

from ergal.profile import Profile


def build_profile():
    profile = Profile(
        'Test API Profile',
        base='https://httpbin.org',
        test=True)
    
    return profile


class TestProfile:
    """ All tests for the profile module and Profile class. """
    def test_init(self):
        profile = build_profile()
        assert type(profile) is Profile

        profile = Profile(1, base=1, test=True)
        assert profile.name == 'default'
        assert profile.base == 'default'

        profile.db.close()
        os.remove('ergal_test.db')

    def test_call(self):
        profile = build_profile()
        profile.add_endpoint('JSON', '/json', 'get')
        profile.add_endpoint('XML', '/xml', 'get')

        assert type(profile.call('JSON')) is dict
        assert type(profile.call('XML')) is dict

        profile.db.close()
        os.remove('ergal_test.db')
    
    def test_set_auth(self):
        profile = build_profile()
        assert type(profile) is Profile

        profile.set_auth('header', name='test', key='test')
        assert profile.auth == {
            'method': 'header',
            'name': 'test',
            'key': 'test'}

        profile.db.close()
        os.remove('ergal_test.db')

    def test_add_endpoint(self):
        profile = build_profile()
        assert type(profile) is Profile

        profile.add_endpoint('Test', '/test', 'get')
        assert profile.endpoints == {
            'Test': {
                'path': '/test',
                'method': 'get'}}
        
        profile.db.close()
        os.remove('ergal_test.db')
    
    def test_del_endpoint(self):
        profile = build_profile()
        assert type(profile) is Profile

        profile.add_endpoint('Test', '/test', 'get')
        assert profile.endpoints == {
            'Test': {
                'path': '/test',
                'method': 'get'}}
        
        profile.del_endpoint('Test')
        assert profile.endpoints == {}
        
        profile.db.close()
        os.remove('ergal_test.db')

