
# coding=utf-8
import json
import itertools as it

import pytest

from tempo.recurrentevent import RecurrentEvent
# noinspection PyProtectedMember
from tempo.recurrenteventset import (AND, NOT, OR, _walk, RecurrentEventSet, Void)

from tempo.unit import Unit
from tests.data import DATA_FOR_TESTING_CONTAINS, DATA_FOR_TESTING_FORWARD


def callback(op, *args):
    assert all(isinstance(arg, bool) for arg in args)
    if op == AND:
        return all(args)
    elif op == OR:
        return any(args)
    elif op == NOT:
        assert len(args) == 1
        return not args[0]
    else:
        raise AssertionError


@pytest.mark.parametrize('expression, callback, expected', [
    ((AND, True, True), callback, True),
    ((AND, True, False), callback, False),
    ((OR, True, False), callback, True),
    ((OR, False, False), callback, False),
    ((NOT, False), callback, True),
    ((NOT, True), callback, False),
    ((AND, (OR, False, (NOT, False), True, (NOT, False))),
     callback, True),
    ((AND, (OR, False, (NOT, False), True, (NOT, True))),
     callback, True),
    ((AND, (NOT, True), True, (AND, False, (NOT, False))),
     callback, False),
    ((AND, (NOT, False), True, (AND, True, (NOT, False))),
     callback, True),
    ([AND, [NOT, False], True, [AND, True, [NOT, False]]],
     callback, True),
])
def test_walk(expression, callback, expected):
    """Cases for expression evaluator - '_walk' function."""
    assert _walk(expression, callback) == expected


def test_walk_raises_void():
    """If result of evaluation is empty, Void is raised."""
    expression = (OR, True, False)

    def callback(*_):
        raise Void

    with pytest.raises(Void):
        _walk(expression, callback)


@pytest.mark.parametrize('first, second, expected', [
    (RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 3, 'hour', 'day'))
     )),
     RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 3, 'hour', 'day'))
     )),
     True),
    (RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 3, 'hour', 'day'))
     )),
     RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 4, 'hour', 'day'))
     )),
     False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)


def test_eq_with_other_type():
    """Equality for object with othery type should not throw exceptions
    and return False."""
    recurrenteventset = RecurrentEventSet.from_json([AND, 0, 10, 'hour', 'day'])
    other = object()

    assert not (recurrenteventset == other)


@pytest.mark.parametrize('item, expression, expected', DATA_FOR_TESTING_CONTAINS)
def test_contains(item, expression, expected):
    """Cases for containment test."""
    assert (item in RecurrentEventSet(expression)) == expected


@pytest.mark.parametrize('recurrenteventset, expected', [
    (RecurrentEventSet(
        [AND, RecurrentEvent(1, 15, Unit.YEAR, None)]
     ),
     [AND, [1, 15, 'year', None]]),
    (RecurrentEventSet(
        [AND, RecurrentEvent(1, 25, Unit.DAY, Unit.WEEK)]
     ),
     [AND, [1, 25, 'day', 'week']]),
    (RecurrentEventSet(
        [AND, RecurrentEvent(5, 25, Unit.YEAR, None),
        [NOT, RecurrentEvent(10, 15, 'year', None)]]
     ),
     [AND, [5, 25, 'year', None], [NOT, [10, 15, 'year', None]]]),
])
def test_to_json(recurrenteventset, expected):
    """Cases for `to_json()` method."""
    actual = recurrenteventset.to_json()

    assert actual == expected


@pytest.mark.parametrize('value, expected', [
    (json.dumps([AND, [0, 15, 'day', 'week']]),
     RecurrentEventSet(
         [AND, RecurrentEvent(0, 15, Unit.DAY, Unit.WEEK)]
     )),
    (json.dumps([AND, [5, 25, 'year', None]]),
     RecurrentEventSet([AND, RecurrentEvent(5, 25, Unit.YEAR, None)])),
    ([AND, [5, 25, 'year', None]],
     RecurrentEventSet([AND, RecurrentEvent(5, 25, Unit.YEAR, None)])),
    ([AND, [5, 25, 'year', None], [NOT, [10, 15, 'year', None]]],
     RecurrentEventSet(
         [AND, RecurrentEvent(5, 25, Unit.YEAR, None),
          [NOT, RecurrentEvent(10, 15, 'year', None)]]
     ))
])
def test_from_json(value, expected):
    """Cases for `from_json()` method."""
    actual = RecurrentEventSet.from_json(value)

    assert actual == expected


@pytest.mark.parametrize('expression, start, trim, expected', DATA_FOR_TESTING_FORWARD)
def test_forward(expression, start, trim, expected):
    """Various forward() cases."""
    actual = list(it.islice(RecurrentEventSet.from_json(expression).forward(start, trim), len(expected)))

    print(actual)
    print(expected)
    assert actual == expected


@pytest.mark.parametrize('expression, expected', [
    ([AND, [1, 5, "month", "year"], [NOT, [1, 15, "day", "month"]]], True),
    ([AND, [1, 2, "months", "year"]], False),
    ('["AND", [1, 2, "month", "year"]]', True),
    ([AND, ['one', 2, "month", "year"]], False),
    ([AND, [1, 'two', "month", "year"]], False),
    (['and', [1, 2, "month", "year"]], True),
    ([AND, [1, 2, 12, "year"]], False),
    ([AND, [1, 2, "month", 100]], False),
])
def test_validate_json(expression, expected):
    """Cases for RecurrentEventSet.validate_json()."""
    assert RecurrentEventSet.validate_json(expression) == expected


# @pytest.mark.timeout(5)
# @pytest.mark.parametrize('expression, start, trim, expected', DATA_FOR_TESTING_FORWARD)
# def test_forward_in_a_for_loop(expression, start, trim, expected):
#     """Various forward() cases."""
#     for index, start_end_tuple in enumerate(RecurrentEventSet.from_json(expression).forward(start, trim)):
#         print(start_end_tuple)
#         print(expected[index])
#         start_end_tuple = expected[index]
#         assert start_end_tuple == expected[index]


@pytest.mark.timeout(5)
@pytest.mark.parametrize('expression, start, trim, expected', DATA_FOR_TESTING_FORWARD)
def test_forward_in_a_for_loop(expression, start, trim, expected):
    """Various forward() cases."""
    recurrent_event_set = RecurrentEventSet.from_json(['AND', [1, 7, 'day', 'week'], [8, 17, 'hour', 'day']])
    for start, end in recurrent_event_set.forward(start):
        print(start, end)
        assert start
        assert end
