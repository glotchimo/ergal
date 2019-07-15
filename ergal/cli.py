"""
ergal.cli
~~~~~~~~~

This module implements the command line interface for Ergal.
"""

import os
import sys
import asyncio

from .profile import Profile

clear = lambda: os.system("cls" if os.name == "nt" else "clear")


def main():
    clear()

    print("Welcome to the Ergal CLI.")

    name = input("\nEnter the name of a Profile to get/create: ")
    profile = Profile(name, logs=True)

    main_menu(profile)


def main_menu(profile):
    clear()

    action = input(
        f"""Current Profile: {profile.name}\n
    Management Options (enter corresponding number)

        1. Authentication management    4. Profile management
        2. Endpoint management          5. Change profile
        3. Data target management       6. Quit

    """
    )

    if action == "1":
        auth_menu(profile)
    elif action == "2":
        endpoint_menu(profile)
    elif action == "3":
        input("\nAction not supported! Press enter to return.")
        main_menu(profile)
    elif action == "4":
        profile_menu(profile)
    elif action == "5":
        main()
    elif action == "6":
        clear()
        sys.exit()


##############################
#
#   Authentication Management
#
##############################
def auth_menu(profile):
    clear()

    action = input(
        f"""Current Profile: {profile.name}\n
    Authentication Management (enter corresponding number)

        1. View Authentication
        2. Add authentication
        3. Return to the main menu

    """
    )

    if action == "1":
        auth_view(profile)
    elif action == "2":
        auth_add(profile)
    elif action == "3":
        main_menu(profile)


def auth_view(profile):
    print(f"\nAuthentication Data for {profile.name}: \n")
    print(profile.auth)

    input("\nPress enter to return to the authentication management menu.")
    auth_menu(profile)


def auth_add(profile):
    clear()

    method = input("\nAuthentication Method: ")
    if method == "basic":
        username = input("\nUsername: ")
        password = input("Password: ")
        profile.add_auth(method, username=username, password=password)

        main_menu(profile)
    elif method == "params":
        name = input("\nName: ")
        value = input("Value: ")
        profile.add_auth(method, name=name, value=value)

        main_menu(profile)
    elif method == "headers":
        name = input("\nName: ")
        value = input("Value: ")
        profile.add_auth(method, name=name, value=value)

        main_menu(profile)
    elif method == "":
        input("\nPress enter to return to the authentication management menu.")
        auth_menu(profile)
    else:
        print('\nInvalid method. Try "basic", "params", or "headers".')
        auth_add(profile)


#########################
#
#   Endpoint Management
#
#########################
def endpoint_menu(profile):
    clear()

    action = input(
        f"""Current Profile: {profile.name}\n
    Endpoint management (enter corresponding number)

        1. View endpoints               4. Add endpoint
        2. Delete endpoint              5. Return to the main menu
        3. Update endpoint

    """
    )

    if action == "1":
        endpoint_view(profile)
    elif action == "2":
        endpoint_delete(profile)
    elif action == "3":
        endpoint_update(profile)
    elif action == "4":
        endpoint_add(profile)
    elif action == "5":
        main_menu(profile)


def endpoint_view(profile):
    print("\nDisplaying endpoints...\n")
    print(profile.endpoints)

    input(
        "\nEndpoints displayed, press enter to return to the endpoint management menu."
    )

    endpoint_menu(profile)


def endpoint_delete(profile):
    endpoint = input("\nEndpoint to Delete: ")

    profile.del_endpoint(endpoint)

    input("\nPress enter to return to the endpoint management menu.")

    endpoint_menu(profile)


def endpoint_update(profile):
    input(
        "\nThis feature is not yet supported! Press enter to return to the endpoint management menu."
    )
    endpoint_menu(profile)


def endpoint_add(profile):
    name = input("\nName: ")
    path = input("Path from Base: ")
    method = input("Request Method: ")

    profile.add_endpoint(name, path, method)

    input("\nPress enter to return to the endpoint management menu.")
    endpoint_menu(profile)


#######################
#
#   Profile Management
#
#######################
def profile_menu(profile):
    clear()

    action = input(
        f"""Current Profile: {profile.name}\n
    URL Management (enter corresponding number)

        1. View URL
        2. Change URL
        3. Return to the main menu

    """
    )

    if action == "1":
        url_view(profile)
    elif action == "2":
        url_change(profile)
    elif action == "3":
        main_menu(profile)


def url_view(profile):
    print("\nThe current base URL is: ", profile.base)

    input("\nPress enter to return to the URL management menu")

    profile_menu(profile)


def url_change(profile):
    clear()

    url = profile.base

    if url:
        new = input(
            "\nThe current base URL is: "
            + url
            + ", what would you like to set the  URL to? Leave blank to cancel.\n"
        )
    else:
        new = input(
            "\nThere is no current base URL for this profile, what would you like to set the URL to? Leave blank to cancel.\n"
        )

    if new == "":
        print("Canceled.")
    else:
        profile.base = new
        profile.update()

    input("\nPress enter to return to the main menu")
    profile_menu(profile)


if __name__ == "__main__":
    main()
