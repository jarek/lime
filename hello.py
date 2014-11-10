#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, desc
import os
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    # define fields
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    person = db.Column(db.String, index = True)
    merchant = db.Column(db.String, index = True)
    notes = db.Column(db.Text)
    category = db.Column(db.String, index = True)
    account = db.Column(db.String, index = True)
    bankAmount = db.Column(db.Float)
    bankCurrency = db.Column(db.String)
    transactionAmount = db.Column(db.Float)
    transactionCurrency = db.Column(db.String)

    def __init__(self, row):
        # straightforward text fields
        self.person = row['person']
        self.merchant = row['merchant']
        self.notes = row['notes']
        self.category = row['category']
        self.account = row['account']
        self.bankCurrency = row['bankCurrency']
        self.transactionCurrency = row['transactionCurrency']

        # parse datetime from string
        try:
            self.date = datetime.datetime.strptime(row['date'], '%Y/%m/%d %H:%M:%S')
        except:
            try:
                self.date = datetime.datetime.strptime(row['date'], '%Y/%m/%d')
            except:
                print 'could not parse ' + row['date']
                pass

        # parse numeric amounts
        try:
            self.bankAmount = float(row['bankAmount'])
        except:
            pass

        try:
            self.transactionAmount = float(row['transactionAmount'])
        except:
            pass

    def __repr__(self):
        return '<Transaction at %s for %s>' % (self.date, self.bankAmount)

@app.route('/')
def hello_world():
    joint = Transaction.query.filter_by(person='')

    sums = Transaction.query.add_columns(func.sum(Transaction.bankAmount).label('sum')).group_by(Transaction.person).all()

    sumsByAccount = joint.add_columns(func.sum(Transaction.bankAmount).label('sum')).group_by(Transaction.account).order_by(desc('sum')).all()

    return '<br/>'.join([str(s[0].person) + str(s[1]) for s in sums]) + '<br/>' + '<br/>'.join([str(s[0].account) + ' : ' + str(s[1]) for s in sumsByAccount])
    #return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

