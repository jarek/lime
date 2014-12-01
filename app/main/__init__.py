#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
