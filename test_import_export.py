#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import unittest
from flask import current_app
import setup
from app import create_app, db, csv
from app.models import Transaction

TEST_CSV = 'testinput.csv'
TEST_SQLITE = 'tests.sqlite'

# requires:
# - that a TEST_SQLITE file exists in app directory - easiest to copy an existing database
# - that a TEST_CSV valid import CSV is specified and exists in root directory
#   - must not have row headings or empty lines
#   - newlines must be \n with no newline after last entry in the file
#   - effective exchange rate row must not be included
#   - all fields must be quoted
# This can be done in gnumeric with Data -> Export Data -> Export into Other Format
# and choosing Text (configurable) with Line Termination: Unix and Quoting: Always
# TODO: come up with a more sensible test rather than just comparing CSV files

class ImportExportTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TEST_SQLITE)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # drop everything currently in the database and recreate/reimport
        db.drop_all()
        db.create_all()        
        setup.import_csv(TEST_CSV)

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_some_data_exists(self):
        self.assertGreater(len(Transaction.query.all()), 0)

    def test_export_is_same_as_import(self):
        with open(TEST_CSV, 'rb') as csvfile:
            original = csvfile.read()

        new = csv.transactions_to_csv_string(Transaction.query.all())

        # uncomment to dump new string to file for testing
        """
        with open('new' + TEST_CSV, 'wb') as csvfile:
            csvfile.write(new)
        #"""

        self.assertEqual(original, new)

if __name__ == '__main__':
    unittest.main()

