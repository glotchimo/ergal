"""
ergal.gui.gui
~~~~~~~~~~~~~

This module implements the Flask app setup for the Ergal GUI.
"""

import os
import sqlite3

from ergal.profile import Profile
from ergal.utils import get_db

from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=b'af^6j9(1l)f4b.&a')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/profiles')
    def profiles():
        cursor = get_db()[1]

        sql = "SELECT * FROM Profile"
        cursor.execute(sql)

        records = cursor.fetchall()
        profiles = []
        for record in records:
            profile = Profile(record[1])
            profiles.append(profile)

        context = {'profiles': profiles}
        return render_template('profiles.html', **context)

    @app.route('/profile/<name>')
    def profile(name):
        profile = Profile(name)
        endpoints = profile.endpoints.items()

        context = {'profile': profile, 'endpoints': endpoints}
        return render_template('profile.html', **context)

    return app

