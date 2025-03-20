import datetime


def check_datetime(date):
    if isinstance(date, datetime.date):
        date = datetime.datetime.combine(date, datetime.time.min)

    if datetime.datetime.now() > date:
        return False

    return True
