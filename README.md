ERGAL
=====

Ever dealt with a bunch of API clients? Whether they be methods in your own code, or an abundance of external libraries, dealing with multiple APIs in one application can get messy.

ERGAL, the Elegant and Redable General API Library, is the solution
to your API client problems. By using API profiles stored in a 
lightweight SQLite database, the user can access any API with ease
by supplying just a few key details.

Goals
-----

- Abstract API handling
- Clean up codebases
- Get money

Standard Installation
---------------------

    pip install ergal

### Requirements
- [Python 3.7](https://www.python.org/downloads/)

Quickstart
-----------

### Profile Creation
Before we can access an API (we'll use httpbin in this case), we have to add an `API Profile`. To create an `API profile`, we'll use the `Profile` class from `ergal.profile`.

    >>> from ergal.profile import Profile
    >>> profile = Profile('JSON Placeholder API', base='https://httbin.org')

A new row has been created in the local `ergal.db` database file to house the API profile's information.

Now that the profile has been created, we'll need to add an endpoint, and to do so, we'll use the `add_endpoint` method, and supply it with a `name`, `path`, and `method`.

    >>> profile.add_endpoint('list posts', '/posts', 'get')
    Endpoint 'list posts' for JSON Placeholder API added at ab0b5ffa9fa95c6.

With an endpoint added, we can make the call. To do that, we'll use the `call` method. All we need to supply is the name of the endpoint we just added, and ERGAL will do the rest.

    >>> profile.call('list posts')
    {big dict of response data}

Hooray! Now we can do whatever we want with our cleaned up and easy-to-work-with dictionary.


Contribution
------------

The biggest priority of this project is to make API handling simple, both on the client's side and ERGAL's side. That said, some protocol can get pretty complex. We've got a few major improvements on our roadmap, and contribution is always appreciated.

As per most open source projects, submitted code needs to be continuous with the rest in style, it needs to be as succinct and readable as it can be, and it has to serve a real purpose according to the objectives of this project.

### Feature Ideas

#### OAuth 1.0a and OAuth 2
OAuth 2 is obviously the priority here, given its increase in popularity, however, we want to provide as much compatability as possible. ERGAL is supposed to be a one-stop solution!

#### HTML
Though virtually every API uses JSON or XML to send response data, what may be useful is the parsing of HTML in the context of a scraping library. In the same sense, often times lots of code needs to be written to support scrapers of multiple sites, so having HTML compatability would be useful.

#### Targetted Parsing
One of the original feature ideas for ERGAL was the targetted parsing of responses, i.e. one could specify on a given endpoint what data should be returned. This would, of course, further eliminate what parsing needs to be done on the client's end by abstracting it within ERGAL.

### Development Setup

    git clone https://github.com/elliott-maguire/ergal
    cd ergal
    pyenv local 3.7.1
    poetry install

### Requirements
- [Python 3.7](https://www.python.org/downloads/)
- [poetry](https://github.com/sdispater/poetry) (a package/version manager for humans)

### Recommended Tools
- [pyenv](https://github.com/pyenv/pyenv) (preferred venv manager)
