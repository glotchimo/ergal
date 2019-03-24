"""
ergal.cli
~~~~~~~~~

This module implements the command line interface for Ergal.
"""

import os
import asyncio

from .profile import Profile

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')


def main():
    clear()

    print('Welcome to the Ergal CLI.')

    name = input('\nEnter the name of a Profile to get/create: ')
    profile = Profile(name, logs=True)

    action = input("""
    Management Options (enter corresponding number)

        1. Add authentication           4. Add a data target
        2. Add an endpoint              5. Delete a data target
        3. Delete an endpoint
    """)

    if action == '1':
        add_auth(profile)


def add_auth(profile):
    clear()

    method = input('Method: ')
    if method == 'basic':
        username = input('Username: ')
        password = input('Password: ')
        asyncio.run(profile.add_auth(
            method, username=username, password=password))

        main()
    elif method == 'params':
        name = input('Name: ')
        value = input('Value: ')
        asyncio.run(profile.add_auth(
            method, name=name, value=value))

        main()
    elif method == 'headers':
        name = input('Name: ')
        value = input('Value: ')
        asyncio.run(profile.add_auth(
            method, name=name, value=value))

        main()
    else:
        print('Invalid method. Try "basic", "params", or "headers".')
        add_auth(profile)


if __name__ == "__main__":
    main()

