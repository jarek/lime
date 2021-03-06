#!/usr/bin/env python2
# coding=utf-8

from __future__ import unicode_literals
import os
from flask.ext.script import Manager, Shell
#from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app, db, csv
from app.models import Transaction, TransactionForm


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
#migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Transaction=Transaction, TransactionForm=TransactionForm)

manager.add_command("shell", Shell(make_context=make_shell_context))
#manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

# this functionality is now also available via web in app/main/views.py : import_from_csv()
@manager.command
def setup(source_file):
    # create database if not present
    db.create_all()

    # import file contents
    with open(source_file, 'rb') as csvfile:
        csv.db_populate_from_csv_iterable(csvfile)


if __name__ == '__main__':
    manager.run()

