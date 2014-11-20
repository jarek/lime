#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, desc
import os
import datetime


db = SQLAlchemy()

def create_app(database_file = 'data.sqlite'):
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, database_file)
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    
    db.init_app(app)

    return app

