Ergal
=====
[![Build Status](https://travis-ci.com/rlygud/ergal.svg?branch=master)](https://travis-ci.com/rlygud/ergal) <img alt="GitHub" src="https://img.shields.io/github/license/rlygud/ergal.svg">

API integrations can be cumbersome and messy, and Ergal makes this process cleaner and more efficient by enabling the user to create, manage, and access simple API profiles stored in a lightweight SQLite database.

The Ergal calling structure is also fully async, making it significantly faster and more efficient than traditional linear implementations.

*Ergal is a derivation of the Greek word εργαλείο (ergaleío), meaning tool.*

Goals
-----

- Concise integrations
- Cleaner codebases
- Faster API interactions

Standard Installation
---------------------

    pip install ergal

### Requirements
- [Python 3.7](https://www.python.org/downloads/)

Quickstart
-----------

### Python Shell
Before we can access an API (we'll use `httpbin.com` in this case), we have to add an `API Profile`. To create an `API profile`, we'll use the `Profile` class from `ergal.profile`.

    >>> from ergal import Profile
    >>> profile = Profile('HTTPBin', base='https://httbin.org')
    Profile for 'HTTPBin' created on e74afb669fb45b58a6c742b83f624166.

A new row has been created in the local `ergal.db` database to house the API profile's information.

Now that the profile has been created, we'll need to add an endpoint, and to do so, we'll use the `add_endpoint` method, and supply it with a `name`, `path`, and `method`.

    >>> profile.add_endpoint('Get JSON', '/json', 'get')
    Endpoint 'Get JSON' for 'HTTPBin' added on e74afb669fb45b58a6c742b83f624166.

With an endpoint added, we can make the call. To do that, we'll use the `call` method. All we need to supply is the name of the endpoint we just added, and ergal will do the rest.

    >>> asyncio.run(profile.call('Get JSON'))
    <Response [200]>

Hooray! Now we can do whatever we want with our cleaned up and easy-to-work-with dictionary of response data.

### Ergal CLI
You can also now use the Ergal CLI:

    $ python -m ergal.cli

Contribution
------------

As per most open source projects, submitted code needs to be continuous with the rest in style, it needs to be as succinct and readable as it can be, and it has to serve a real purpose according to the objectives of this project.

### Development Setup

First, fork the master repository. Then, do this:

    git clone https://github.com/<your username>/ergal
    cd ergal
    poetry install

### Development Requirements
- [Python 3.7](https://www.python.org/downloads/)
- [poetry](https://github.com/sdispater/poetry) (a package/version manager for humans)

### Recommended Tools
- [pyenv](https://github.com/pyenv/pyenv) (preferred venv manager)
