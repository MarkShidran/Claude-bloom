import datetime


def get_year_start(d: datetime.date) -> datetime.date:
    return datetime.date(d.year, 1, 1)


def get_quarter_end(d: datetime.date) -> datetime.date:
    quarter = (d.month - 1) // 3
    month = (quarter + 1) * 3
    if month == 3:
        return datetime.date(d.year, 3, 31)
    elif month == 6:
        return datetime.date(d.year, 6, 30)
    elif month == 9:
        return datetime.date(d.year, 9, 30)
    else:
        return datetime.date(d.year, 12, 31)


def years_ago(n: int, from_date: datetime.date | None = None) -> datetime.date:
    from_date = from_date or datetime.date.today()
    return datetime.date(from_date.year - n, from_date.month, from_date.day)


def format_date_ru(d: datetime.date) -> str:
    return d.strftime("%d.%m.%Y")
