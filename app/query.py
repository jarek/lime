#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from collections import defaultdict
import sqlalchemy
from sqlalchemy.sql import func, desc
from . import db
from models import Transaction


def get_field_by_name(field_name):
    if isinstance(field_name, sqlalchemy.orm.attributes.InstrumentedAttribute):
        return field_name
    else:
        field = getattr(Transaction, field_name, None)

        if isinstance(field, sqlalchemy.orm.attributes.InstrumentedAttribute):
            return field
        else:
            return None

def all():
    return db.session.query()

def for_field(field_name):
    return db.session.query(get_field_by_name(field_name))

def group(group_by_field, query = None):
    field = get_field_by_name(group_by_field)

    if query is None:
        query = for_field(field)

    if field is None:
        return query
    else:
        return query.add_columns(func.sum(Transaction.bankAmount).label('sum')) \
                    .group_by(field).order_by(desc('sum'))

def group_count(group_by_field, query = None):
    field = get_field_by_name(group_by_field)

    if query is None:
        query = for_field(field)

    if field is None:
        return query
    else:
        return query.add_columns(func.count(field).label('count')) \
                    .group_by(field).order_by(desc('count'))

def group_format(group_by_field, query = None):
    field = get_field_by_name(group_by_field)

    if field is None:
        return []

    sums = group(field, query)

    return [{'key': s[0],
             'keyname': field.name, \
             'filter': {field.name: s[0]}, \
             'amount': s[1] if s[1] is not None else 0} for s in sums]

