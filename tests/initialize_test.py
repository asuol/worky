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

from worky.storage import Storage, StorageException
import pytest
import os


def init_with_exception(db_path):
    with pytest.raises(StorageException) as error:
        Storage(db_path)

    assert error.type is StorageException


def test_empty_path():
    db_path = ""

    init_with_exception(db_path)


def test_whitespace_path():
    db_path = " "

    init_with_exception(db_path)


def test_dot_path():
    db_path = "."

    init_with_exception(db_path)


def test_slash_path():
    db_path = "/"

    init_with_exception(db_path)


def test_simple_path(tmpdir):
    db_path = str(tmpdir.join("stuff.worky"))

    assert not os.path.isfile(db_path)

    Storage(db_path)

    assert os.path.isfile(db_path)

    os.remove(db_path)


def test_db_in_dir(tmpdir):
    db_path = str(tmpdir.mkdir("db").join("stuff.worky"))

    assert not os.path.isfile(db_path)

    Storage(db_path)

    assert os.path.isfile(db_path)

    os.remove(db_path)
