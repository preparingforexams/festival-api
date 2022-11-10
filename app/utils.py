from datetime import datetime
from typing import List, Optional, Callable

from .logger import create_logger


def log(function: Callable):
    def wrapper(*args, **kwargs):
        logger = create_logger(function.__name__)
        logger.debug("start")

        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger.error("exception thrown", exc_info=True)
            raise e
        finally:
            logger.debug("end")

    return wrapper


@log
def parse_date(date_string: str, date_formats: List[str] = None, default_year: int = 2023) -> Optional[datetime]:
    date = None
    if date_formats is None:
        date_formats = ["%d.%m", "%d.%m.%Y"]

    for date_format in date_formats:
        try:
            date = datetime.strptime(date_string, date_format)
        except ValueError as e:
            pass

    if date:
        if date.year == 1900:
            date = date.replace(year=default_year)

    return date

