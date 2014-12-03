#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from collections import defaultdict
from datetime import datetime
import flask
from sqlalchemy.sql import func
from . import main
from .. import db, csv, query
from ..models import Transaction, TransactionForm


def make_template_data(grouped_data, description = None):
    for grouped in grouped_data:
        grouped['other'] = [f for f in Transaction.CLASSIFICATION_FIELDS if f != grouped['keyname']]
        grouped['description'] = description

    return grouped_data

@main.route('/api/groups/')
def get_groups():
    data = Transaction.query

    filters = flask.request.args.get('query', '')
    if filters != '':
        filters = flask.json.loads(filters)
        data = data.filter_by(**filters) #.filter(Transaction.date >= '2014-11-01')

    group_by = flask.request.args['group_by'] # this is required so KeyError on missing is okay
    data = query.group_format(data, group_by)

    return flask.jsonify({'groups': data})

@main.route('/api/transactions/')
def get_transactions():
    data = Transaction.query

    filters = flask.request.args.get('query', '')
    if filters != '':
        filters = flask.json.loads(filters)
        data = data.filter_by(**filters) #.filter(Transaction.date >= '2014-11-01')

    transactions = [t.to_dict() for t in data]

    return flask.jsonify({'transactions': transactions})

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
            make_template_data(query.group_format(Transaction.query, Transaction.person), "per person"),
            make_template_data(query.group_format(joint, Transaction.account), "joint transactions by account"),
            make_template_data(query.group_format(Transaction.query, Transaction.category), "all transactions by category"),
            make_template_data(query.group_format(joint.filter_by(account='cash'), Transaction.category), "cash transactions"),
            make_template_data(query.group_format(Transaction.query, Transaction.merchant)[:20], "top 20 merchants")
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

    allCategories = query.get_unique(Transaction.query, Transaction.category)
    allCurrencies = query.get_unique(Transaction.query, Transaction.transactionCurrency)

    # prepopulate currency with most common currency
    form.transactionCurrency.data = allCurrencies[0] if len(allCurrencies) > 0 else None

    return flask.render_template('index.html', form = form,
        allCategories = allCategories, allCurrencies = allCurrencies)

