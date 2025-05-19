"""
MIT License

Copyright (c) 2020 André Lousa Marques <andre.lousa.marques at gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from worky.storage import Storage
import pytest
from datetime import datetime, timedelta, UTC

due_date_format = '%Y-%m-%d'


@pytest.fixture
def _setup(tmpdir):
    db_path = str(tmpdir.join("stuff.worky"))

    yield Storage(db_path)


def _create_active_task(storage):
    description = "sample task"

    due_date = datetime.now(UTC) + timedelta(days=1)
    due_date = due_date.strftime(due_date_format)

    storage.create_task(description, due_date)

    assert len(storage.get_active_tasks()) == 1
    assert len(storage.get_overdue_tasks()) == 0
    assert len(storage.get_completed_tasks()) == 0

    active_task = storage.get_active_tasks()[0]

    assert active_task.description == description
    assert active_task.due_date.strftime(due_date_format) == due_date

    return (description, due_date, active_task)


def _create_overdue_task(storage):
    description = "sample task"

    due_date = datetime.now(UTC) - timedelta(days=1)
    due_date = due_date.strftime(due_date_format)

    storage.create_task(description, due_date)

    assert len(storage.get_active_tasks()) == 0
    assert len(storage.get_overdue_tasks()) == 1
    assert len(storage.get_completed_tasks()) == 0

    overdue_task = storage.get_overdue_tasks()[0]

    assert overdue_task.description == description
    assert overdue_task.due_date.strftime(due_date_format) == due_date

    return (description, due_date, overdue_task)


def _complete_task(storage, description, due_date, task):
    storage.complete_task(task.id)

    assert len(storage.get_active_tasks()) == 0
    assert len(storage.get_overdue_tasks()) == 0
    assert len(storage.get_completed_tasks()) == 1

    completed_task = storage.get_completed_tasks()[0]

    assert completed_task[0].description == description
    assert completed_task[0].due_date.strftime(due_date_format) == due_date

    t1_completed_by = completed_task[1].completed_by.strftime(due_date_format)

    assert t1_completed_by == datetime.now(UTC).strftime(due_date_format)

    return completed_task


def _assert_no_tasks(storage):
    assert storage.get_active_tasks() == []
    assert storage.get_overdue_tasks() == []
    assert storage.get_completed_tasks() == []


def test_get_task(_setup):
    storage = _setup

    _assert_no_tasks(storage)


def test_create_active_task(_setup):
    storage = _setup

    _create_active_task(storage)


def test_create_overdue_task(_setup):
    storage = _setup

    _create_overdue_task(storage)


def test_create_completed_active_task(_setup):
    storage = _setup

    (description, due_date, active_task) = _create_active_task(storage)

    _complete_task(storage, description, due_date, active_task)


def test_create_completed_overdue_task(_setup):
    storage = _setup

    (description, due_date, overdue_task) = _create_overdue_task(storage)

    _complete_task(storage, description, due_date, overdue_task)


def test_delete_active_task(_setup):
    storage = _setup

    (_, _, active_task) = _create_active_task(storage)

    storage.delete_task(active_task.id)

    _assert_no_tasks(storage)


def test_delete_overdue_task(_setup):
    storage = _setup

    (_, _, overdue_task) = _create_overdue_task(storage)

    storage.delete_task(overdue_task.id)

    _assert_no_tasks(storage)


def test_delete_completed_active_task(_setup):
    storage = _setup

    (description, due_date, active_task) = _create_active_task(storage)

    completed_task = _complete_task(storage, description, due_date,
                                    active_task)

    storage.delete_task(completed_task[0].id)

    _assert_no_tasks(storage)
