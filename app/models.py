#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import datetime
import wtforms
import sqlalchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import wtf
from . import db

class Transaction(db.Model):
    # row titles/names as stored in source/export CSV
    CSV_ROW_TITLES = ['date','person','merchant','notes','category','account','bankAmount','bankCurrency','transactionAmount','transactionCurrency']

    # CLASSIFICATION_FIELDS are those we can filter list of Transactions by
    CLASSIFICATION_FIELDS = ['date', 'person', 'merchant', 'notes', 'category', 'account', 'bankCurrency', 'transactionCurrency']

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

    def __repr__(self):
        return '<Transaction at %s for %s>' % (self.date, self.bankAmount)

    @sqlalchemy.orm.reconstructor
    def init_on_load(self):
        # fill in transactionCurrency and transactionAmount where not specified
        if not self.transactionCurrency and not self.transactionAmount \
            and self.bankCurrency and self.bankAmount:
            self.transactionCurrency = self.bankCurrency
            self.transactionAmount = self.bankAmount

    def from_dict(self, row):
        # most fields are straightforward strings, import all of those at once
        text_properties = {field: value for field, value in row.items()
            if field not in ['bankAmount', 'transactionAmount', 'date']}

        self.__dict__.update(text_properties)

        # parse datetime from string
        if isinstance(row['date'], datetime.datetime):
            self.date = row['date']
        else:
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

        return self

    def to_dict(self):
        # get a list of object's fields that are in CSV_ROW_TITLES
        result = {field: value for field, value in vars(self).items() if field in self.CSV_ROW_TITLES}

        # ensure formatting of date fields
        if self.date.hour == 0 and self.date.minute == 0 and self.date.second == 0:
            # allow specifying datetimes with date part only
            result['date'] = datetime.datetime.strftime(self.date, '%Y/%m/%d')
        else:
            result['date'] = datetime.datetime.strftime(self.date, '%Y/%m/%d %H:%M:%S')

        # export whole numbers as ints to match input csv formatting
        if self.bankAmount is not None and self.bankAmount == int(self.bankAmount):
            result['bankAmount'] = int(self.bankAmount)
        if self.transactionAmount is not None and self.transactionAmount == int(self.transactionAmount):
            result['transactionAmount'] = int(self.transactionAmount)

        return result

class TransactionForm(wtf.Form):
    transactionAmount = wtforms.DecimalField('Amount', [wtforms.validators.Required(message='An amount is required')])
    merchant = wtforms.StringField('Merchant', [wtforms.validators.Required(message='A merchant name is required')])
    notes = wtforms.StringField('Notes')
    category = wtforms.StringField('Category')
    transactionCurrency = wtforms.StringField('Currency')
    submit = wtforms.SubmitField('Save')

    def to_dict(self):
        return {field: value.data for field, value in vars(self).items() if field in Transaction.CSV_ROW_TITLES}

    def to_transaction(self):
        as_dict = self.to_dict()

        as_dict['date'] = datetime.datetime.now()
        if as_dict.get('bankAmount') == None:
            as_dict['bankAmount'] = as_dict['transactionAmount']
        if as_dict.get('bankCurrency') == None:
            as_dict['bankCurrency'] = as_dict['transactionCurrency']

        return Transaction().from_dict(as_dict)

