from datetime import datetime, timedelta, UTC

due_date_format = '%Y-%m-%d'

datepicker_date_format = '%m%d%Y'


def current_date():
    return datetime.now(UTC).strftime(due_date_format)


def datepicker_current_date():
    return datetime.now(UTC).strftime(datepicker_date_format)


def _date_from_today(days_to_add):
    return datetime.now(UTC) + timedelta(days=days_to_add)


def date_from_today(days_to_add):
    return _date_from_today(days_to_add).strftime(due_date_format)


def datepicker_date_from_today(days_to_add):
    return _date_from_today(days_to_add).strftime(datepicker_date_format)


def datepicker_to_due_date_format(datepicker_date):
    return datetime.strptime(datepicker_date,
                             datepicker_date_format).strftime(due_date_format)
