# coding=utf-8
import os
import logging

import psycopg2
from psycopg2.extensions import cursor as psycopg2_cusror
import pytest

from tests.utils import create_database, drop_database, create_plpythonu, \
    uninstall_postgresql_tempo, install_postgresql_tempo

logger = logging.getLogger('tempo.tests')


class LoggingCursor(psycopg2_cusror):
    """Logs queries and notices."""
    def __init__(self, *args, **kwargs):
        super(LoggingCursor, self).__init__(*args, **kwargs)

    def log(self):
        logger.debug(self.query)

        while len(self.connection.notices) > 0:
            notice = self.connection.notices.pop(0)
            logger.debug(notice)

    def execute(self, *args, **kwargs):
        try:
            return super(LoggingCursor, self).execute(*args, **kwargs)
        finally:
            self.log()

    def callproc(self, *args, **kwargs):
        try:
            return super(LoggingCursor, self).callproc(*args, **kwargs)
        finally:
            self.log()


@pytest.fixture(scope='session')
def connection(request):
    """Creates connection to a test database."""
    host = os.environ['TEMPO_DB_HOST']
    port = os.environ['TEMPO_DB_PORT']
    user = os.environ['TEMPO_DB_USER']
    password = os.environ['TEMPO_DB_PASSWORD']
    database = os.environ['TEMPO_DB_NAME']
    with psycopg2.connect(host=host, port=port, user=user,
                          password=password) as connection_:
        drop_database(connection_, database)
        create_database(connection_, database, user)

    db_connection = psycopg2.connect(host=host, port=port, user=user,
                                     password=password, database=database,
                                     cursor_factory=LoggingCursor)

    def finalize():
        db_connection.close()
        with psycopg2.connect(
                host=host, port=port, user=user, password=password
        ) as connection_:
            connection_.autocommit = True
            drop_database(connection_, database)

    request.addfinalizer(finalize)

    return db_connection


@pytest.fixture()
def transaction(request):
    """Rollbacks transaction after test run.

    Intended to use through `transaction` marker.
    """
    connection_ = request.getfuncargvalue('connection')

    with connection_.cursor() as cursor:
        cursor.execute('SAVEPOINT tempo_test_transaction_begin;')

    def rollback():
        with connection_.cursor() as cursor:
            cursor.execute(
                'ROLLBACK TO SAVEPOINT tempo_test_transaction_begin;'
            )

    request.addfinalizer(rollback)


@pytest.fixture(scope='session')
def postgresql_tempo(request):
    """Python-tempo PostgreSQL binding."""
    connection_ = request.getfuncargvalue('connection')
    create_plpythonu(connection_)
    install_postgresql_tempo(connection_)

    def finalizer():
        uninstall_postgresql_tempo(connection_)

    request.addfinalizer(finalizer)


@pytest.fixture()
def django_postgresql_tempo(request):
    """Python-tempo PostgreSQL binding using Django connection."""
    from django.db import connection as connection_

    create_plpythonu(connection_)
    install_postgresql_tempo(connection_)

    def finalizer():
        uninstall_postgresql_tempo(connection_)

    request.addfinalizer(finalizer)


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        if ({'django_db', 'db', 'connection', 'transaction'} &
            set(item.keywords.keys()) or
            item.name.lower() == 'docs/source/usage.rst'):
            item.add_marker('xfailifnodb')


def pytest_runtest_setup(item):
    transaction_marker = item.get_closest_marker("transaction")
    if transaction_marker is not None:
        item.add_marker(pytest.mark.usefixtures('transaction'))

    if item.get_closest_marker("xfailifnodb") is not None:
        if not ({'TEMPO_DB_HOST',
             'TEMPO_DB_PORT',
             'TEMPO_DB_USER',
             'TEMPO_DB_PASSWORD',
             'TEMPO_DB_NAME'} <=
             set(os.environ.keys())):
            pytest.xfail('Database is not setup.')
