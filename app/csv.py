#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import unicodecsv
from cStringIO import StringIO
from models import Transaction


def transactions_from_csv(f):
    results = []

    reader = unicodecsv.DictReader(f, Transaction.CSV_ROW_TITLES)
    for row in reader:
        results.append(Transaction().from_dict(row))

    return results

def transactions_to_csv(f, all_transactions):
    writer = unicodecsv.DictWriter(f, fieldnames = Transaction.CSV_ROW_TITLES)

    for row in all_transactions:
        writer.writerow(row.to_dict())

    return f

def transactions_to_csv_string(all_transactions):
    f = StringIO()

    return transactions_to_csv(f, all_transactions).getvalue()

