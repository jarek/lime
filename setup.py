#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import argparse
import hello


def detect_db():
    # create database if not present
    try:
        hello.Transaction.query.all()
    except:
        hello.db.create_all()

def import_csv(filename):
    with open(filename, 'rb') as csvfile:
        for transaction in hello.csv.transactions_from_csv(csvfile):
            hello.db.session.add(transaction)

    hello.db.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='name of a CSV file to process')
    args = parser.parse_args()

    with hello.app.app_context():
        detect_db()
        import_csv(args.file)

