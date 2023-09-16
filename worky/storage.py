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

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime
import logging
import re
from sqlalchemy.exc import OperationalError
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logger.setLevel(__debug__)

Base = declarative_base()


class Tasks(Base):
    """
    Tasks table
    """
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    created_date = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, nullable=False)


class Completed(Base):
    """
    Completed Tasks table
    """
    __tablename__ = 'completed'

    id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"),
                primary_key=True)
    completed_by = Column(DateTime, nullable=False)


class Storage():
    """
    Persistent storage
    """

    def __init__(self, db_path):
        """
        Constructor

        Parameters
        ----------
        db_path : str
            path to the database

        Raises
        ------
        StorageException
            if the given database path points to an invalid path or if the
            database does not match the expected schema
        """
        self._due_date_format = '%Y-%m-%d'

        if (not re.search(".*[a-zA-Z]\\w*\\.worky", db_path)):
            raise StorageException("Database name must start with a letter "
                                   "and end with .worky: %s" % db_path)

        try:
            engine = sqlalchemy.create_engine("sqlite:///" + db_path,
                                              poolclass=NullPool)

            self._session_maker = sessionmaker(bind=engine,
                                               expire_on_commit=False)

            """ if the database was just created """
            if sqlalchemy.inspect(engine).get_table_names() == []:
                """ create the database tables """
                Base.metadata.create_all(engine)

            self._validate_database(sqlalchemy.inspect(engine))
        except OperationalError:
            raise StorageException("Invalid database path: %s" % db_path)

    def _validate_database(self, inspector):
        """
        Validates a loaded database against the expected schema

        Parameters
        ----------
        inspector : sqlalchemy.Inspector
            database inspector object

        Raises
        ------
        StorageException
            if the given database does not match the expected schema
        """
        expected_tables = [Tasks.__tablename__, Completed.__tablename__]
        obtained_tables = inspector.get_table_names()
        error_msg = ("The loaded database is not compatible with this "
                     "application")

        # Validate tables
        self._compare_lists(expected_tables, obtained_tables, error_msg)

        # Validate Tasks table columns
        self._inspect_table_columns(inspector, Tasks.__tablename__,
                                    sqlalchemy.inspect(Tasks).columns,
                                    error_msg)
        self._inspect_primary_key(inspector, Tasks.__tablename__, ["id"],
                                  error_msg)
        self._inspect_foreign_key(inspector, Tasks.__tablename__, [],
                                  error_msg)

        # Validate Completed table columns
        self._inspect_table_columns(inspector, Completed.__tablename__,
                                    sqlalchemy.inspect(Completed).columns,
                                    error_msg)
        self._inspect_primary_key(inspector, Completed.__tablename__, ["id"],
                                  error_msg)
        self._inspect_foreign_key(inspector, Completed.__tablename__,
                                  [{"constrained_columns": ["id"],
                                    "referred_table": Tasks.__tablename__,
                                    "referred_columns": ["id"]}], error_msg)

    def _inspect_table_columns(self, inspector, table_name, expected_columns,
                               error_msg):
        """
        Retrieves the column names for a given database table

        Parameters
        ----------
        inspector : sqlalchemy.Inspector
            database inspector object
        table_name : str
            database table name
        expected_columns: list of str
            expected columns on the database table
        error_msg : str
            error message to be used with any raised StorageException

        Raises
        ------
        StorageException
            if the given table primary keys do not match the expected
        """
        table_columns = [c["name"] for c in inspector.get_columns(table_name)]

        self._compare_lists(table_columns, expected_columns, error_msg)

    def _inspect_primary_key(self, inspector, table_name,
                             expected_primary_keys, error_msg):
        """
        Inspects the primary keys for a given database table

        Parameters
        ----------
        inspector : sqlalchemy.Inspector
            database inspector object
        table_name : str
            database table name
        expected_primary_keys : list of str
            expected primary keys for the given database table
        error_msg : str
            error message to be used with any raised StorageException

        Raises
        ------
        StorageException
            if the given table primary keys do not match the expected
        """
        primary_keys = inspector.get_pk_constraint(table_name)

        self._compare_lists(expected_primary_keys,
                            primary_keys["constrained_columns"], error_msg)

    def _inspect_foreign_key(self, inspector, table_name,
                             expected_foreign_keys, error_msg):
        """
        Inspects the foreign keys for a given database table

        Parameters
        ----------
        inspector : sqlalchemy.Inspector
            database inspector object
        table_name : str
            database table name
        expected_foreign_keys : list of dict: {"referred_table": str,
                                            "referred_columns": list of str,
                                            "constrained_columns": list of str}
            expected foreign keys for the given database table
        error_msg : str
            error message to be used with any raised StorageException

        Raises
        ------
        StorageException
            if the given table foreign keys do not match the expected
        """
        foreign_keys = inspector.get_foreign_keys(table_name)

        if len(foreign_keys) != len(expected_foreign_keys):
            raise StorageException(error_msg)

        for expected_key in expected_foreign_keys:
            key = next(fk for fk in foreign_keys
                       if
                       (
                           fk["referred_table"]
                           ==
                           expected_key["referred_table"]
                        )
                       )

            if (
                (
                    len(key["constrained_columns"])
                    !=
                    len(expected_key["constrained_columns"])
                )
                or
                (
                    len(key["referred_columns"])
                    !=
                    len(expected_key["referred_columns"])
                )
            ):
                raise StorageException(error_msg)

            for cc in expected_key["constrained_columns"]:
                if cc not in key["constrained_columns"]:
                    raise StorageException(error_msg)

            for rc in expected_key["referred_columns"]:
                if rc not in key["referred_columns"]:
                    raise StorageException(error_msg)

    def _compare_lists(self, list1, list2, error_msg):
        """
        Compares two lists and raises an exception if they have different
        lengths or do not share the same elements

        Parameters
        ----------
        list1 : list of str
            first list
        list2 : list of str
            second list
        error_msg : str
            error message to be used with any raised StorageException

        Raises
        ------
        StorageException
            if the given lists do not match
        """
        if len(list1) != len(list2):
            raise StorageException(error_msg)

        for element in list1:
            if element not in list2:
                raise StorageException(error_msg)

    def _today(self):
        return datetime.utcnow().strftime(self._due_date_format)

    def _current_date_time(self):
        return datetime.utcnow().replace(microsecond=0)

    @contextmanager
    def _session_scope(self):
        session = self._session_maker()

        try:
            yield session

            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _get_task_query(self, session, task_id):
        """
        Get the task with the provided id

        Parameters
        ----------
        session: sqlalchemy.org.session.Session
            sqlalchemy ORM session object
        task_id: int
            task id

        Returns
        -------
        query: sqlalchemy.query
            the corresponding Task query,
            or None if the given id does not exist
        """
        return session.query(Tasks).filter(Tasks.id == task_id)

    def get_task(self, task_id):
        """
        Get the task with the provided id

        Parameters
        ----------
        task_id: int
            task id

        Returns
        -------
        task: Tasks
            the corresponding Task object,
            or None if the given id does not exist
        """
        with self._session_scope() as session:
            return self._get_task_query(session, task_id).first()

    def _get_incomplete_tasks(self, session):
        """
        Get all the incomplete tasks

        Parameters
        ----------
        session: sqlalchemy.org.session.Session
            sqlalchemy ORM session object

        Returns
        -------
        tasks: list of Tasks
            incomplete tasks
        """
        t = session.query(Tasks)

        tasks = t.outerjoin(Completed, Tasks.id == Completed.id)

        return tasks.filter(Completed.id.is_(None)).order_by(Tasks.due_date)

    def get_active_tasks(self):
        """
        Get all the active tasks (not yet complete, and not overdue)

        Returns
        -------
        tasks: list of Tasks
            active tasks
        """
        with self._session_scope() as session:
            incomplete_tasks = self._get_incomplete_tasks(session)
            query = incomplete_tasks.filter(Tasks.due_date >= self._today())

            return query.all()

    def get_overdue_tasks(self):
        """
        Get all the active overdue tasks

        Returns
        -------
        tasks: list of Tasks
            active overdue tasks
        """
        with self._session_scope() as session:
            incomplete_tasks = self._get_incomplete_tasks(session)
            query = incomplete_tasks.filter(Tasks.due_date < self._today())

            return query.all()

    def get_completed_tasks(self):
        """
        Get all the completed tasks

        Returns
        -------
        tasks: list of Tasks
            completed tasks
        """
        with self._session_scope() as session:
            all_tasks = session.query(Tasks, Completed)
            completed_tasks = all_tasks.filter(Completed.id == Tasks.id)
            query = completed_tasks.order_by(Completed.completed_by.desc())

            return query.all()

    def create_task(self, description, due_date):
        """
        Create new task

        Parameters
        ----------
        description: str
            task description
        due_date: date
            task due date
        """
        due_date = datetime.strptime(due_date, self._due_date_format)

        with self._session_scope() as session:
            task = Tasks(description=description, due_date=due_date,
                         created_date=self._current_date_time(),
                         last_updated=self._current_date_time())
            session.add(task)
            session.commit()

    def update_task(self, task_id, description, due_date):
        """
        Update an existing task

        Parameters
        ----------
        task_id: int
            task id
        description: str
            task description
        due_date: date
            task due date
        """
        due_date = datetime.strptime(due_date, self._due_date_format)

        with self._session_scope() as session:
            task = self._get_task_query(session, task_id).first()

            task.description = description
            task.due_date = due_date
            task.last_updated = self._current_date_time()

    def delete_task(self, task_id):
        """
        Delete a task

        Parameters
        ----------
        task_id: int
            task id
        """
        with self._session_scope() as session:
            self._get_task_query(session, task_id).delete()

    def complete_task(self, task_id):
        """
        Mark a task as completed

        Parameters
        ----------
        task_id: int
            task id
        """
        with self._session_scope() as session:
            complete = Completed(id=task_id,
                                 completed_by=self._current_date_time())

            session.add(complete)


class StorageException(Exception):
    """
    Storage class exception
    """
    pass
