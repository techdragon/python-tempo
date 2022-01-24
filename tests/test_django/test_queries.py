
# coding=utf-8
import datetime as dt
import json
from functools import partial

import pytest

from tempo.recurrentevent import RecurrentEvent

from tempo.recurrenteventset import RecurrentEventSet
from tests import Implementation
from tests.data import DATA_FOR_TESTING_CONTAINS, DATA_FOR_TESTING_FORWARD


def pg_contains(item, expression, connection):
    """PostgreSQL binding RecurrentEventSet containment test
    implementation."""
    if isinstance(item, tuple):
        item = list(item)

    recurrenteventset = RecurrentEventSet(expression).to_json()
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT tempo_recurrenteventset_contains(%s, %s)''',
            (json.dumps(recurrenteventset), item)
        )
        return cursor.fetchone()[0]


def recurrenteventset_contains(request):
    connection = request.getfuncargvalue('connection')
    request.getfuncargvalue('postgresql_tempo')
    request.getfuncargvalue('transaction')
    return partial(pg_contains, connection=connection)


@pytest.mark.xfailifnodb('postgresql')
@pytest.mark.parametrize('item, expression, expected', DATA_FOR_TESTING_CONTAINS)
def test_contains(item, expression, expected, recurrenteventset_contains):
    """Cases for containment test."""
    assert recurrenteventset_contains(item, expression) == expected


def pg_forward(expression, start, trim, n, connection):
    """PostgreSQL API for RecurrentEventSet.forward()."""

    recurrenteventset = RecurrentEventSet.from_json(expression).to_json()
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT * FROM tempo_recurrenteventset_forward(%s, %s, %s, %s)''',
            (json.dumps(recurrenteventset), start, n, trim)
        )

        return list(cursor.fetchall())


@pytest.fixture(params=Implementation.values())
def recurrenteventset_forward(request):
    """Various APIs for RecurrentEventSet.forwars()."""
    connection = request.getfuncargvalue('connection')
    request.getfuncargvalue('postgresql_tempo')
    request.getfuncargvalue('transaction')
    return partial(pg_forward, connection=connection)


@pytest.mark.parametrize('expression, start, trim, expected', DATA_FOR_TESTING_FORWARD)
def test_forward(expression, start, trim, expected, recurrenteventset_forward):
    """Various forward() cases."""
    actual = recurrenteventset_forward(expression, start, trim, len(expected))

    print(actual)
    print(expected)
    assert actual == expected
