#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from collections import OrderedDict
import flask
from sqlalchemy.sql import func
from . import main
from .. import db, csv, query
from ..models import Transaction, TransactionForm, CSVImportForm, ConfirmForm


def make_template_data(processed_data, description = None):
    result = {
        'description': description,
        'data': processed_data
    }

    for key in processed_data:
        list_for_key = processed_data[key]

        if len(list_for_key) == 0:
            continue

        keyname = list_for_key[0]['keyname']
        result['keyname'] = keyname
        others = [f for f in Transaction.CLASSIFICATION_FIELDS if f != keyname]

        for item in list_for_key:
            item['other'] = others

    return result

@main.route('/api/groups/')
def get_groups():
    group_by = flask.request.args['group_by'] # this is required so KeyError on missing is okay
    data = query.for_field(group_by)

    filters = flask.request.args.get('query', '')
    if filters != '':
        filters = flask.json.loads(filters)
        data = data.filter_by(**filters) #.filter(Transaction.date >= '2014-11-01')

    data = query.group_format(group_by, data)

    return flask.jsonify({'groups': data})

@main.route('/api/transactions/')
def get_transactions():
    data = query.all(Transaction).order_by(Transaction.date.asc())

    filters = flask.request.args.get('query', '')
    if filters != '':
        filters = flask.json.loads(filters)
        data = data.filter_by(**filters) #.filter(Transaction.date >= '2014-11-01')

    transactions = [t.to_dict() for t in data]

    return flask.jsonify({'transactions': transactions})

@main.route('/stats/')
def show_stats():
    joint = query.for_field(Transaction.account).filter_by(person='')

    timespan = query.all() \
        .add_columns(func.max(Transaction.date).label('maxDate')) \
        .add_columns(func.min(Transaction.date).label('minDate'))
    datespan = timespan[0][0] - timespan[0][1]

    merchants = query.group_format(Transaction.merchant)
    top_merchants = OrderedDict()
    for key in merchants.keys()[0:20]:
        top_merchants[key] = merchants[key]

    amount_data = [
        make_template_data(query.group_format(Transaction.person), "per person"),
        make_template_data(query.group_format(Transaction.account, joint), "joint transactions by account"),
        make_template_data(query.group_format(Transaction.category), "all transactions by category"),
        make_template_data(top_merchants, "top 20 merchants")
    ]

    return flask.render_template('stats.html',
                                 datespan=datespan,
                                 number_of_days=datespan.total_seconds() / (60*60*24),
                                 number_of_months=datespan.total_seconds() / (60*60*24*30),
                                 amount_data=amount_data)

@main.route('/export/')
def export_csv():
    return csv.transactions_to_csv_string(query.all(Transaction).order_by(Transaction.date.asc()))

@main.route('/import/', methods = ['GET', 'POST'])
def import_from_csv():
    try:
        db.create_all()
    except:
        return flask.render_template('error.html', hide_nav = True, hide_footer = True,
            error_message_title = 'cannot find database, are you sure it exists?',
            error_message = 'Try to CREATE DATABASE')

    form = CSVImportForm()

    # check form, call csv.db_populate_from_csv_iterable with contents
    if flask.request.method == 'POST':
        if form.validate_on_submit():
            # encode('utf8') is needed because unicodecsv works on bytestrings
            # http://stackoverflow.com/questions/21479589
            lines = [line.rstrip().encode('utf8') for line in form.lines.data.split('\n')]
            csv.db_populate_from_csv_iterable(lines)
            flask.flash('Imported %d transactions' % len(lines))
            return flask.redirect(flask.url_for('.index'))

    # table found or created, can proceed to import
    return flask.render_template('import.html', hide_nav = True, form = form)

@main.route('/clear/', methods = ['GET', 'POST'])
def clear_db():
    form = ConfirmForm()
    form.confirm.label = 'Remove all transactions'

    if flask.request.method == 'POST':
        if form.validate_on_submit() and form.confirm.data == True:
            deleted_rows = query.all(Transaction).delete()
            flask.flash('%d transactions deleted' % deleted_rows)
            return flask.redirect(flask.url_for('.index'))

    return flask.render_template('confirm.html', confirm_title = 'Confirm clearing database', form = form)

@main.route('/', methods = ['GET', 'POST'])
def index():
    try:
        # try to cause error if the table is not present
        query.for_field(Transaction.category).first()
    except:
        # redirect to setup page if table is not present
        return flask.redirect(flask.url_for('.import_from_csv'))

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

    allCurrencies = [s[0] for s in query.group_count(Transaction.transactionCurrency)]
    allCategories = [s[0] for s in query.group_count(Transaction.category)]

    # prepopulate currency with most common currency
    form.transactionCurrency.data = allCurrencies[0] if len(allCurrencies) > 0 else None

    return flask.render_template('index.html', form = form,
        allCategories = allCategories, allCurrencies = allCurrencies)

