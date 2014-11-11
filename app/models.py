#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from . import db

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

