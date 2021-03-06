#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('LIME_SECRET_KEY') or '03fde23919b25d59cbdb8feef8e31396af7a707b'
    WEB_PASSWORD = os.environ.get('LIME_WEB_PASSWORD')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    # sqlite connection strings look like:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://pg_lime_dev:password@localhost/pg_lime_dev'
    WEB_PASSWORD = os.environ.get('LIME_WEB_PASSWORD') or 'F5Yanm43k29b8Q'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://pg_lime_test:password@localhost/pg_lime_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

