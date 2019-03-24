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

    root_menu(profile)


def root_menu(profile):

    clear()
    action = input("""
    Management Options (enter corresponding number)

        1. Authentication management    4. URL management
        2. Endpoint management          5. Change profiles
        3. Data target management       6. <N/A>
    """)

    if action == '1':
        auth_manage(profile)
    elif action == '2':
        endpoint_manage(profile)
    elif action == '3':
        input('\nAction not supported! Press enter to return...')
        root_menu(profile)
    elif action == '4':
        url_manage(profile)
    elif action == '5':
        main()

###########################
#
#   Authentication section
#
###########################
def auth_manage(profile):
    clear()

    endpoint_action = input("""\n
    Authentication management (enter corresponding number)

        1. View Authentication
        2. Add authentication
        3. Return to the main menu
    
    """)

    if endpoint_action == '1':
        auth_view(profile)
    elif endpoint_action == '2':
        auth_add(profile)
    elif endpoint_action == '3':
        root_menu(profile)

def auth_view(profile):
    print('\n Current authentication: ' + profile.auth)

    input('\nPress enter to return to the authentication management menu...')
    auth_manage(profile)

def auth_add(profile):
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
        auth_add(profile)


###########################
#
#   Endpoint section
#
###########################
def endpoint_manage(profile):
    clear()

    endpoint_action = input("""\n
    Endpoint management (enter corresponding number)

        1. View endpoints
        2. Delete endpoint
        3. Update endpoint
        4. Add endpoint 
        5. Return to the main menu
    
    """)

    if endpoint_action == '1':
        endpoint_view(profile)
    elif endpoint_action == '2':
        endpoint_delete(profile)
    elif endpoint_action == '3':
        endpoint_update(profile)
    elif endpoint_action == '4':
        endpoint_add(profile)
    elif endpoint_action == '5':
        root_menu(profile)

def endpoint_view(profile):
    
    print("\nDisplaying endpoints....")
    print(profile.endpoints)
    input("\nEndpoints displayed, press enter to return to the endpoint management menu")
    endpoint_manage(profile)

def endpoint_delete(profile):
    
    deletion_target = input('\nWhat endpoint would you like to delete?\n')
    
    asyncio.run(profile.del_endpoint(
        deletion_target))
    
    input("\nEndpoint deleted! Press enter to return to the endpoint management menu")

    endpoint_manage(profile)

def endpoint_update(profile):
    input('\nThis feature is not yet supported! Press enter to return to the endpoint management menu!')
    endpoint_manage(profile)

def endpoint_add(profile):

    ep_name = input('\nWhat would you like to name this end point?\n')

    ep_url = input('\nWhat is the path to this end point? (Do not include the base url)\n')
    
    ep_method = input('\nWhat is the type of request method this end point uses?\n')

    asyncio.run(profile.add_endpoint(
        ep_name, ep_url, ep_method))

    input("\nEnd point added, press enter to return to the endpoint management menu")
    endpoint_manage(profile)


###########################
#
#   URL section
#
###########################
def url_manage(profile):
    clear()

    url_action = input("""\n
    Url management (enter corresponding number)

        1. View URL
        2. Change URL
        3. Return to the main menu
    """)

    if url_action == '1':
        url_view(profile)
    elif url_action == '2':
        url_change(profile)
    elif url_action == '3':
        root_menu(profile)

def url_view(profile):

    print('\n The current URL is: ' + profile.base)
        
    input('\n Press enter to return to the URL management menu')
    url_manage(profile)

def url_change(profile):
    clear()

    cur_url = profile.base

    if cur_url:
       new_url = input("The current  URL is: " + cur_url + ", what would you like to set the  URL to? Leave blank to cancel\n")
    else:     
       new_url = input("There is no current URL for this profile, what would you like to set the URL to? Leave blank to cancel\n")

    if new_url == "":
        print('Canceled...')

    else:
        profile.base = new_url
        profile.update()
        print('Updated...')

    input("\nPress enter to return to the main menu")
    url_manage(profile)





if __name__ == "__main__":
    main()