#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import flask

main = flask.Blueprint('main', __name__)

from . import views

@main.before_request
def check_valid_login():
    # basic - require auth for all pages for now

    # per http://stackoverflow.com/questions/13428708/best-way-to-make-flask-logins-login-required-the-default
    # and http://flask.pocoo.org/snippets/8/

    needed_password = flask.current_app.config['WEB_PASSWORD']
    login_valid = flask.request.authorization and needed_password \
        and flask.request.authorization.password == needed_password

    if not login_valid and not flask.request.endpoint.startswith('static'):
        return flask.Response('You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

