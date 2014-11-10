#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
import argparse
import unicodecsv
import hello


def detect_db():
    # create database if not present
    try:
        hello.Transaction.query.all()
    except:
        hello.db.create_all()

def import_csv(filename):
    ROW_TITLES = ['date','person','merchant','notes','category','account','bankAmount','bankCurrency','transactionAmount','transactionCurrency','effective exchange rate']
    with open(filename, 'rb') as csvfile:
        reader = unicodecsv.DictReader(csvfile, ROW_TITLES)
        for row in reader:
            hello.db.session.add(hello.Transaction(row))

    hello.db.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='name of a CSV file to process')
    args = parser.parse_args()

    detect_db()
    import_csv(args.file)

