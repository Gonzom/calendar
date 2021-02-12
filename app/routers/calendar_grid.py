from calendar import Calendar, day_name
from datetime import date, datetime, time, timedelta
import itertools
import locale
from typing import Dict, Iterator, List, Sequence, Tuple

import pytz

from app.dependencies import logger

MONTH_BLOCK: int = 6

# TODO: connect to the user's language setting
locale.setlocale(locale.LC_TIME, ("en", "UTF-8"))


class Day:
    """A Day class.

    Args:
        date_of_day: The datetime of the day.

    Attributes:
        date: The datetime of the day.
        name: The day's name.
        full_day_events: List of tuples representing a full day event
            in the format of: [("", "")]  # TODO: fill in format
        events: List of tuples representing a timed event in the format of:
            [("09AP", "Meeting with yam")]
        css: The day's CSS styling.

    """

    def __init__(self, date_of_day: datetime):
        self.date: datetime = date_of_day
        self.name: str = self.date.strftime("%A")
        self.full_day_events: List[Tuple[str, str]] = []
        self.events: List[Tuple[str, str]] = []
        self.css: Dict[str, str] = {
            'day_container': 'day',
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily',
                'front',
                'background-warmyellow',
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray',
            ]),
            'event': 'event',
        }

    def __str__(self) -> str:
        return self.date.strftime("%d")

    def get_short_date(self) -> str:
        """Returns the day date in the format of "DD MONTH YY".

        For example: 03 MAY 88

        """
        return self.date.strftime("%d %B %y").upper()

    def get_id(self) -> str:
        """Returns the day date in the format of "DD-Month-YYYY".

        For example: 03-May-1988

        """
        return self.date.strftime("%d-%b-%Y")

    @staticmethod
    def get_user_local_time() -> datetime:
        """
        Returns the user's local time.

        Localizes the time based on Greenwich time.

        Returns:
            The user's local time.

        """
        greenwich = pytz.timezone('GB')
        return greenwich.localize(datetime.now())

    @staticmethod
    def convert_str_to_date(date_string: str) -> datetime:
        """Returns a datetime object from a string.

        If the string is not a valid date logs and raises an exception.

        Args:
            date_string: A date in string format.

        Returns:
            A datetime object.

        Raises:
            ValueError: If not a valid string format.

        """
        try:
            return datetime.strptime(date_string, '%d-%b-%Y')
        except ValueError as error:
            logger.critical(error)
            raise error

    @staticmethod
    def is_weekend(current_date: date) -> bool:
        """Returns True if the day is a weekend.

        Args:
            current_date: The current date.

        Returns:
            True if a weekend date, False if otherwise.

        """
        return current_date.strftime("%A") in Week.DAYS_OF_THE_WEEK[-2:]


class DayWeekend(Day):
    """A DayWeekend class.

    Args:
        date_of_day: The datetime of the day.

    """

    def __init__(self, date_of_day: datetime):
        super().__init__(date_of_day)
        self.css = {
            'day_container': 'day ',
            'date': ' '.join(['day-number', 'text-gray']),
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily',
                'front',
                'background-warmyellow',
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray',
            ]),
            'event': 'event',
        }


class Today(Day):
    """A Today class.

    Args:
        date_of_day: The datetime of the day.

    """

    def __init__(self, date_of_day: datetime):
        super().__init__(date_of_day)
        self.css = {
            'day_container': ' '.join([
                'day',
                'text-darkblue',
                'background-yellow',
            ]),
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily',
                'front',
                'text-lightgray',
                'background-darkblue',
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray',
            ]),
            'event': 'event',
        }


class FirstDayMonth(Day):
    """A FirstDayMonth class.

    Args:
        date_of_day: The datetime of the day.

    """

    def __init__(self, date_of_day: datetime):
        super().__init__(date_of_day)
        self.css = {
            'day_container': ' '.join([
                'day',
                'text-darkblue',
                'background-lightgray',
            ]),
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily front',
                'text-lightgray',
                'background-red',
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray',
            ]),
            'event': 'event',
        }

    def __str__(self) -> str:
        return self.date.strftime("%d %b %y").upper()


class Week:
    """A Week class.

    Args:
        days: A list of Days.

    """
    WEEK_DAYS: int = 7
    DAYS_OF_THE_WEEK: Sequence[str] = day_name

    def __init__(self, days: List[Day]):
        self.days: List[Day] = days


def get_day(calendar_date: datetime) -> Day:
    """Returns the Day object according to the given date.

    Args:
        calendar_date: The given calendar date.

    Returns:
        A Day object of the correct type.

    """
    if calendar_date == date.today():
        return Today(calendar_date)
    if int(calendar_date.day) == 1:
        return FirstDayMonth(calendar_date)
    if Day.is_weekend(calendar_date):
        return DayWeekend(calendar_date)
    return Day(calendar_date)


def get_days_from_date(start_date: datetime, number_of_days: int
                       ) -> Iterator[Day]:
    """Generates a set amount of Days from an initial start date.

    Args:
        start_date: The start date from where to generate Days.
        number_of_days: The requested range of Days.

    Yields:
        A Day object.

    """
    next_date_generator = _get_next_day(start_date)
    yield from itertools.islice(next_date_generator, number_of_days)


def get_weeks(days: List[Day], week_length: int = Week.WEEK_DAYS
              ) -> List[Week]:
    """Returns a list of Weeks objects.

    Args:
        days: A list of Days.
        week_length: Optional; The number of days in the week.

    Returns:
        A list of Weeks.

    """
    total_number_of_days: int = len(days)
    return [Week(days[i:i + week_length])
            for i in range(0, total_number_of_days, week_length)]


def get_month_block(day: Day, number_of_weeks: int = MONTH_BLOCK
                    ) -> List[Week]:
    """Returns a list of Weeks for the current month.

    Using the default value of MONTH_BLOCK, the layout will show a 6 week view.

    Args:
        day: The current Day.
        number_of_weeks: Optional; The number of weeks to show in the layout.

    Returns:
        A list of Weeks for the current month.

    """
    current_date = _get_first_day_month_block(day.date) - timedelta(days=1)
    number_of_days = Week.WEEK_DAYS * number_of_weeks
    return get_weeks(list(get_days_from_date(current_date, number_of_days)))


def _get_next_day(starting_date: datetime) -> Iterator[Day]:
    """Generates date objects from a starting given date.

    Args:
        starting_date: The starting date from where to generate Days.

    """
    yield from (
        get_day(starting_date + timedelta(days=i))
        for i in itertools.count(start=1)
    )


def _get_first_day_month_block(calendar_date: datetime) -> datetime:
    """Returns the first date in a month block of given date.

    Args:
        calendar_date: A datetime of a given date.

    Returns:
        A datetime object of the first date of a month.

    """
    month = list(Calendar().itermonthdates(
        calendar_date.year, calendar_date.month))

    return datetime.combine(month[0], time.min)


# TODO: is this used other than in a test?
def get_date_before_n_days(calendar_date: datetime, number_of_days: int
                           ) -> datetime:
    """Returns the date before a set amount of days.

    Args:
        calendar_date: A datetime of a given date.
        number_of_days: The number of days before the calendar_date
            for which to retrieve a datetime object.

    Returns:
        The date of the day set an N amount of days before
        the date passed as the argument.

    """
    return calendar_date - timedelta(days=number_of_days)
