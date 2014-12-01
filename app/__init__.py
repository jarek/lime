#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, desc
import os
import datetime
from config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # this import needs to be here to avoid circular dependencies
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    db.init_app(app)

    return app

