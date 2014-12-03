#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from collections import defaultdict
import sqlalchemy
from sqlalchemy.sql import func, desc
from models import Transaction


def get_field_by_name(field_name):
    if isinstance(field_name, sqlalchemy.orm.attributes.InstrumentedAttribute):
        return field_name
    else:
        transaction_fields = vars(Transaction)

        if field_name in transaction_fields and isinstance(transaction_fields[field_name], sqlalchemy.orm.attributes.InstrumentedAttribute):
            return transaction_fields[field_name]
        else:
            return None

def group(query, group_by_field):
    field = get_field_by_name(group_by_field)

    if field is None:
        return query
    else:
        return query.add_columns(func.sum(Transaction.bankAmount).label('sum' + field.name))\
                    .group_by(field).order_by(desc('sum' + field.name))

def group_format(query, group_by_field):
    field = get_field_by_name(group_by_field)

    if field is None:
        return []

    sums = group(query, field)

    return [{'key': getattr(s[0], field.name), \
             'keyname': field.name, \
             #'data': s[0], \
             'amount': s[1] if s[1] is not None else 0} for s in sums]

def get_unique(query, group_by):
    grouped = query.group_by(group_by).add_columns(func.count().label('count')).order_by(desc('count'))

    # sort by the count
    # this is complicated by the fact that for bankCurrency/transactionCurrency,
    # the database - and the query above - often doesn't have info for transactionCurrency,
    # it is filled in in the object. so we have to loop over objects and group them again.
    # TODO: easier way to do this? or require transactionCurrency to always be set in db?
    sums = defaultdict(int)
    for t in grouped:
        name = getattr(t[0], group_by.name)
        sums[name] += t[1]

    # sort by count t[1] and return names t[0]
    return [t[0] for t in sorted(sums.items(), key=lambda t: t[1], reverse = True)]

