import datetime as dt

from tempo.recurrentevent import RecurrentEvent
from tempo.recurrenteventset import AND, NOT, OR

DATA_FOR_TESTING_CONTAINS = [
    (
        dt.datetime(2005, 5, 15),
        (AND, RecurrentEvent(2, 8, 'month', 'year')),
        True
    ),
    (
        dt.datetime(2005, 12, 15),
        (AND, RecurrentEvent(2, 8, 'month', 'year')),
        False
    ),
    (
        dt.datetime(2005, 5, 15),
        (AND, RecurrentEvent(2, 8, 'month', 'year'), (NOT, RecurrentEvent(4, 5, 'month', 'year'))),
        True
    ),
]


DATA_FOR_TESTING_FORWARD = [
    (
        [OR, [1, 15, 'day', 'month'], [15, 20, 'day', 'month']],
        dt.datetime(2000, 1, 1),
        True,
        [
            (dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 20)),
            (dt.datetime(2000, 2, 1), dt.datetime(2000, 2, 20))
        ]
    ),
    (
        [AND, [1, 15, 'day', 'month'], [10, 20, 'day', 'month']],
        dt.datetime(2000, 1, 1),
        True,
        [
            (dt.datetime(2000, 1, 10), dt.datetime(2000, 1, 15)),
            (dt.datetime(2000, 2, 10), dt.datetime(2000, 2, 15))
        ]
    ),
    (
        [AND, [1, 25, 'day', 'month'], [NOT, [10, 15, 'day', 'month']]],
        dt.datetime(2000, 1, 1),
        True,
        [
            (dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 10)),
            (dt.datetime(2000, 1, 15), dt.datetime(2000, 1, 25))
        ]
    ),
    (
        [AND, [1, 10, 'day', 'month'], [15, 20, 'day', 'month']],
        dt.datetime(2000, 1, 1),
        True,
        []
    ),
    (
        [AND, [5, 10, 'day', 'month'], [15, 20, 'hour', 'day']],
        dt.datetime(2000, 1, 1),
        True,
        [
            (dt.datetime(2000, 1, 5, 15), dt.datetime(2000, 1, 5, 20)),
            (dt.datetime(2000, 1, 6, 15), dt.datetime(2000, 1, 6, 20))
        ]
    ),
    (
        [OR, [5, 10, 'day', 'month']],
        dt.datetime(2000, 1, 8),
        False,
        [
            (dt.datetime(2000, 1, 5), dt.datetime(2000, 1, 10)),
            (dt.datetime(2000, 2, 5), dt.datetime(2000, 2, 10)),
        ]
    ),
    (
        (
            OR,
            (AND, [1, 4, 'day', 'week'], [10, 19, 'hour', 'day']),
            (AND, [5, 6, 'day', 'week'], [10, 16, 'hour', 'day'])
        ),
        dt.datetime(2000, 1, 1),
        False,
        [
            (dt.datetime(2000, 1, 3, 10, 0), dt.datetime(2000, 1, 3, 19, 0)),
            (dt.datetime(2000, 1, 4, 10, 0), dt.datetime(2000, 1, 4, 19, 0)),
            (dt.datetime(2000, 1, 5, 10, 0), dt.datetime(2000, 1, 5, 19, 0))
        ]
    )
]
