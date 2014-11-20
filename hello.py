#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, desc
from app import create_app, db, csv
from app.models import Transaction


app = create_app()


def group(query, group_by):
    field_name = str(group_by).replace('Transaction.', '')
    sums = query.add_columns(func.sum(Transaction.bankAmount).label('sum'))\
        .group_by(group_by).order_by(desc('sum'))

    return [{'key': getattr(s[0], field_name), \
             'keyname': field_name, \
             'data': s[0], \
             'amount': s[1] if s[1] is not None else 0} for s in sums]

def make_template_data(grouped_data):
    for grouped in grouped_data:
        grouped['other'] = [f for f in Transaction.CLASSIFICATION_FIELDS if f != grouped['keyname']]

    return grouped_data

@app.route('/stats/')
def show_stats():
    joint = Transaction.query.filter_by(person='')

    return render_template('stats.html',
        amount_categories = [
            make_template_data(group(Transaction.query, Transaction.person)),
            make_template_data(group(joint, Transaction.account)),
            make_template_data(group(Transaction.query, Transaction.category)),
            make_template_data(group(Transaction.query, Transaction.merchant)[:20])])

@app.route('/export/')
def export_csv():
    return csv.transactions_to_csv_string(Transaction.query.all())

@app.route('/')
def show_home():
    return 'Hello world!'

if __name__ == '__main__':
    app.run(debug=True)

