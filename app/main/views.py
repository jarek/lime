#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from collections import defaultdict
from datetime import datetime
import flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, desc
from . import main
from .. import db, csv
from ..models import Transaction, TransactionForm


def group(query, group_by):
    field_name = group_by.name.replace('Transaction.', '')
    sums = query.add_columns(func.sum(Transaction.bankAmount).label('sum'))\
        .group_by(group_by).order_by(desc('sum'))

    return [{'key': getattr(s[0], field_name), \
             'keyname': field_name, \
             'data': s[0], \
             'amount': s[1] if s[1] is not None else 0} for s in sums]

def make_template_data(grouped_data, description = None):
    for grouped in grouped_data:
        grouped['other'] = [f for f in Transaction.CLASSIFICATION_FIELDS if f != grouped['keyname']]
        grouped['description'] = description

    return grouped_data

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

@main.route('/stats/')
def show_stats():
    # TODO: this needs currency awareness. currently missing all non-GBP-denominated-or-converted
    # transactions, which isn't too bad since it's mostly cash stuff but still.

    joint = Transaction.query.filter_by(person='').filter_by(bankCurrency = 'GBP')

    timespan = Transaction.query \
        .add_columns(func.max(Transaction.date).label('maxDate')) \
        .add_columns(func.min(Transaction.date).label('minDate'))
    datespan = timespan[0][1] - timespan[0][2]

    return flask.render_template('stats.html',
        datespan = datespan,
        number_of_days = datespan.total_seconds() / (60*60*24),
        number_of_months = datespan.total_seconds() / (60*60*24*30),
        amount_categories = [
            make_template_data(group(Transaction.query, Transaction.person), "per person"),
            make_template_data(group(joint, Transaction.account), "joint transactions by account"),
            make_template_data(group(Transaction.query, Transaction.category), "all transactions by category"),
            make_template_data(group(joint.filter_by(account='cash'), Transaction.category), "cash transactions"),
            make_template_data(group(Transaction.query, Transaction.merchant)[:20], "top 20 merchants")
        ])

@main.route('/export/')
def export_csv():
    return csv.transactions_to_csv_string(Transaction.query.all())

@main.route('/', methods = ['GET', 'POST'])
def index():
    form = TransactionForm()

    if flask.request.method == 'POST':
        if form.validate_on_submit():
            transaction = form.to_transaction()
            db.session.add(transaction)
            flask.flash('Transaction added')
            return flask.redirect(flask.url_for('.index'))
        else:
            # debug
            for fieldName, errorMessages in form.errors.iteritems():
                for err in errorMessages:
                    print fieldName, err

    allCategories = get_unique(Transaction.query, Transaction.category)
    allCurrencies = get_unique(Transaction.query, Transaction.transactionCurrency)

    # prepopulate currency with most common currency
    form.transactionCurrency.data = allCurrencies[0] if len(allCurrencies) > 0 else None

    return flask.render_template('index.html', form = form,
        allCategories = allCategories, allCurrencies = allCurrencies)

