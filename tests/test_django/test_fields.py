#!/usr/bin/env python
# coding=utf-8
import datetime as dt

import pytest

from tests.test_django.aproject.anapp.models import AModel, NullableModel
from tempo.timeintervalset import TimeIntervalSet


@pytest.mark.django_db
@pytest.mark.usefixtures('django_postgresql_tempo')
@pytest.mark.parametrize('expression, datetime, expected', [
    (["OR", [1, 15, "day", "month"]], dt.datetime(2000, 1, 10), True),
    (["OR", [1, 15, "day", "month"]], dt.datetime(2000, 1, 30), False),
])
def test_contains(expression, datetime, expected):
    """'contains' lookup."""
    timeintervalset = TimeIntervalSet.from_json(expression)
    expected_object = AModel.objects.create(schedule=timeintervalset)

    objects = AModel.objects.filter(schedule__contains=datetime)

    assert (len(objects) == 1) == expected

    if not expected:
      return

    assert objects[0] == expected_object


@pytest.mark.django_db
@pytest.mark.usefixtures('django_postgresql_tempo')
@pytest.mark.parametrize('expression, start, stop, expected', [
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 15), True),
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 5), False),
])
def test_intersects(expression, start, stop, expected):
    """'intersects' lookup."""
    timeintervalset = TimeIntervalSet.from_json(expression)
    expected_object = AModel.objects.create(schedule=timeintervalset)

    objects = AModel.objects.filter(schedule__intersects=(start, stop))

    assert (len(objects) == 1) == expected

    if not expected:
      return

    assert objects[0] == expected_object


@pytest.mark.django_db
@pytest.mark.usefixtures('django_postgresql_tempo')
@pytest.mark.parametrize('expression, start, stop, expected', [
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 25), True),
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 5), False),
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 25), dt.datetime(2000, 1, 28), False),
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 15), False),
    (["OR", [10, 20, "day", "month"]],
     dt.datetime(2000, 1, 15), dt.datetime(2000, 1, 25), False),
])
def test_occurs_within(expression, start, stop, expected):
    """'occurs_within' lookup."""
    timeintervalset = TimeIntervalSet.from_json(expression)
    expected_object = AModel.objects.create(schedule=timeintervalset)

    objects = AModel.objects.filter(schedule__occurs_within=(start, stop))

    assert (len(objects) == 1) == expected

    if not expected:
      return

    assert objects[0] == expected_object


@pytest.mark.django_db
@pytest.mark.usefixtures('django_postgresql_tempo')
def test_null():
    """null=true option for the field works as expected."""
    NullableModel.objects.create()

    actual = NullableModel.objects.get()

    assert actual.schedule is None
