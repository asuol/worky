from datetime import datetime, timedelta

due_date_format = '%Y-%m-%d'

datepicker_date_format = '%m%d%Y'


def current_date():
    return datetime.utcnow().strftime(due_date_format)


def datepicker_current_date():
    return datetime.utcnow().strftime(datepicker_date_format)


def _date_from_today(days_to_add):
    return datetime.utcnow() + timedelta(days=days_to_add)


def date_from_today(days_to_add):
    return _date_from_today(days_to_add).strftime(due_date_format)


def datepicker_date_from_today(days_to_add):
    return _date_from_today(days_to_add).strftime(datepicker_date_format)
