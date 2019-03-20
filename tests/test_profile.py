"""
tests.test_profile
~~~~~~~~~~~~~~~~~~

This module implements unit tests for the profile module.
"""

import os
import asyncio
import collections

from ergal.profile import Profile

import requests


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

        os.remove('ergal_test.db')

    return wrapper


def build_profile():
    profile = Profile(
        'httpbin',
        base='https://httpbin.org',
        test=True)

    return profile


class TestProfile:
    """ All tests for the profile module and Profile class. """
    @async_test
    async def test_init(self):
        profile =  build_profile()
        assert type(profile) is Profile

        profile = Profile(1, base=1, test=True)
        assert profile.name == 'default'
        assert profile.base == 'default'

        profile.db.close()

    @async_test
    async def test_update(self):
        profile = build_profile()

        profile.base = 'http://httpbin.org'
        profile.update()
        del profile

        profile = Profile('httpbin', test=True)
        assert profile.base == 'http://httpbin.org'

        profile.db.close()

    @async_test
    async def test_delete(self):
        profile = build_profile()
        profile.delete()

        profile = Profile('httpbin', 'http://httpbin.org', test=True)
        assert profile.base == 'http://httpbin.org'

    @async_test
    async def test_call(self):
        profile = build_profile()

        await profile.add_endpoint('GET', '/get', 'GET')
        await profile.add_endpoint('POST', '/post', 'POST')
        await profile.add_endpoint('PUT', '/put', 'PUT')
        await profile.add_endpoint('PATCH', '/patch', 'PATCH')
        await profile.add_endpoint('DELETE', '/delete', 'DELETE')
        await profile.add_endpoint(
            'JSON', '/json', 'GET',
            parse=True)
        await profile.add_target('JSON', 'author')

        response = await profile.call('GET')
        assert type(response) is requests.models.Response
        assert response.status_code == 200

        response = await profile.call('POST')
        assert type(response) is requests.models.Response
        assert response.status_code == 200

        response = await profile.call('PUT')
        assert type(response) is requests.models.Response
        assert response.status_code == 200

        response = await profile.call('PATCH')
        assert type(response) is requests.models.Response
        assert response.status_code == 200

        response = await profile.call('DELETE')
        assert type(response) is requests.models.Response
        assert response.status_code == 200

        data = await profile.call('JSON')
        assert type(data) is dict
        assert 'author' in data

        profile.db.close()

    @async_test
    async def test_add_auth(self):
        profile = build_profile()

        await profile.add_auth('headers', name='Authorization', value='Bearer test')

        assert profile.auth == {
            'method': 'headers',
            'name': 'Authorization',
            'value': 'Bearer test'}

        await profile.add_endpoint(
            'Bearer', '/bearer', 'GET',
            auth=True)

        response = await profile.call('Bearer')
        assert response.status_code == 200

        profile.db.close()

    @async_test
    async def test_add_endpoint(self):
        profile = build_profile()

        await profile.add_endpoint('GET', '/get', 'GET')
        await profile.add_endpoint(
            'JSON', '/json', 'GET',
            parse=True)

        assert profile.endpoints == {
            'GET': {
                'path': '/get', 'method': 'GET'},
            'JSON': {
                'path': '/json', 'method': 'GET',
                'parse': True}}

        profile.db.close()

    @async_test
    async def test_del_endpoint(self):
        profile = build_profile()

        await profile.add_endpoint('GET', '/get', 'GET')
        await profile.del_endpoint('GET')

        assert profile.endpoints == {}

    @async_test
    async def test_add_target(self):
        profile = build_profile()

        await profile.add_endpoint('GET', '/get', 'GET')
        await profile.add_target('GET', 'test')

        assert profile.endpoints == {
            'GET': {
                'path': '/get',
                'method': 'GET',
                'targets': ['test']}}

    @async_test
    async def test_del_target(self):
        profile = build_profile()

        await profile.add_endpoint('GET', '/get', 'GET')
        await profile.add_target('GET', 'test')
        await profile.del_target('GET', 'test')

        assert profile.endpoints == {
            'GET': {
                'path': '/get',
                'method': 'GET',
                'targets': []}}

