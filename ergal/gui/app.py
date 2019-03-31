"""
ergal.gui.gui
~~~~~~~~~~~~~

This module implements the Flask app setup for the Ergal GUI.
"""

import os
import asyncio
import sqlite3

from ergal.profile import Profile
from ergal.utils import get_db

from flask import Flask, request, render_template, redirect, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=b'af^6j9(1l)f4b.&a')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route(
        '/',
        methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route(
        '/profiles',
        methods=['GET'])
    def profiles():
        """ Collects and renders all profiles. """
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

    @app.route(
        '/profiles/add',
        methods=['POST'])
    def add_profile():
        """ Accepts data to create a new profile. """
        form = request.form

        profile = Profile(
            form.get('name'),
            base=form.get('base'))

        return redirect(
            url_for('view_profile', profile_name=profile.name))

    @app.route(
        '/profiles/<profile_name>/view',
        methods=['GET'])
    def view_profile(profile_name):
        """ Renders the view page. """
        profile = Profile(profile_name)

        context = {
            'profile': profile,
            'endpoints': profile.endpoints.items()}
        return render_template('view.html', **context)

    @app.route(
        '/profiles/<profile_name>/edit',
        methods=['GET', 'POST'])
    def edit_profile(profile_name):
        """ Renders the edit page, accepts changes. """
        profile = Profile(profile_name)

        if request.method == 'POST':
            form = request.form

            profile.base = form.get('base')

            profile.update()

        context = {
            'profile': profile,
            'endpoints': profile.endpoints.items()}
        return render_template('edit.html', **context)

    @app.route(
        '/profiles/<profile_name>/delete',
        methods=['GET'])
    def delete_profile(profile_name):
        """ Deletes a profile. """
        profile = Profile(profile_name)

        profile.delete()

        return redirect(url_for('profiles'))

    @app.route(
        '/profiles/<profile_name>/endpoints/add',
        methods=['POST'])
    def add_endpoint(profile_name):
        """ Accepts data to create a new endpoint. """
        form = request.form

        profile = Profile(profile_name)

        asyncio.run(profile.add_endpoint(
            form.get('name'),
            form.get('path'),
            form.get('method'),
            **form))

        return redirect(
            url_for('edit_profile', profile_name=profile.name))

    @app.route(
        '/profiles/<profile_name>/endpoints/<endpoint_name>/edit',
        methods=['POST'])
    def edit_endpoint(profile_name, endpoint_name):
        """ Accepts changes. """
        form = request.form

        profile = Profile(profile_name)
        endpoint = (
            profile.endpoints[endpoint_name]
            if endpoint_name in profile.endpoints
            else None)

        for k, v in form:
            if k in list(endpoint.keys()):
                endpoint[k] = v

        return redirect(
            url_for('edit_profile', profile_name=profile.name))

    return app

