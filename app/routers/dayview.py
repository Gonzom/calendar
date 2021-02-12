from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database.models import Event, User
from app.dependencies import get_db, logger, templates
from app.internal import zodiac
from app.internal.utils import get_placeholder_user

router = APIRouter()


class DivAttributes:
    """A DivAttributes class.

    Args:
        event: The user's Event.
        current_date: Optional; The current date.

    Attributes:
        start_time: The start time of the Event.
        end_time: The end time of the Event.
        length: The length of the Event.
        start_multiday: A flag for whether or not the Event starts
            before the current day.
        end_multiday: A flag for whether or not the Event ends
            before the current day.
        color: The color of the Event.
        total_time: The total time of the Event in a string format.
        grid_position: The position of the Event on the calendar grid.

    """
    GRID_BAR_QUARTER = 1
    FULL_GRID_BAR = 4
    MIN_MINUTES = 0
    MAX_MINUTES = 15
    BASE_GRID_BAR = 5
    FIRST_GRID_BAR = 1
    LAST_GRID_BAR = 101
    DEFAULT_COLOR = "grey"
    DEFAULT_FORMAT = "%H:%M"
    MULTIDAY_FORMAT = "%d/%m %H:%M"

    def __init__(self, event: Event, current_date: datetime = None):
        self.start_time: datetime = event.start
        self.end_time: datetime = event.end
        self.length: float = self._get_event_length()
        self.current_date: Optional[datetime] = current_date
        self.start_multiday: bool
        self.end_multiday: bool
        self.start_multiday, self.end_multiday = self._is_multiday_event()
        self.color: str = event.color or DivAttributes.DEFAULT_COLOR
        self.total_time: str = self._get_total_time()
        self.grid_position: str = self._get_grid_position()

    def _get_event_length(self) -> float:
        """Returns the length of the event."""
        length = self.end_time - self.start_time
        return length.seconds / 60

    def _is_multiday_event(self) -> Tuple[bool, bool]:
        """Returns a tuple of booleans if the event spans more than one day.

        The event is a multiday event if the start day is set before the
        current date, or if the end date is set after the current date.

        Returns:
            A tuple of booleans representing the start_time and end_time
            multiday state of the event.

        """
        start_multiday = False
        end_multiday = False
        if self.current_date:
            if self.start_time < self.current_date:
                start_multiday = True
            self.current_date += timedelta(hours=24)
            if self.current_date <= self.end_time:
                end_multiday = True
        return start_multiday, end_multiday

    def _get_total_time(self) -> str:
        """Returns the total time of the event in string format."""
        start_time_format = self._get_time_format(self.start_multiday)
        start_time = self.start_time.strftime(start_time_format)

        end_time_format = self._get_time_format(self.end_multiday)
        end_time = self.end_time.strftime(end_time_format)

        return ' '.join([start_time, '-', end_time])

    @staticmethod
    def _get_time_format(is_multiday: bool) -> str:
        """Returns the time string format.

        If the event is a multiday event, the string format used
        is MULTIDAY_FORMAT, otherwise it uses DEFAULT_FORMAT.

        Args:
            is_multiday: A flag stating if the date is a multiday event.

        Returns:
            The time format to use.

        """
        if is_multiday:
            return DivAttributes.MULTIDAY_FORMAT
        return DivAttributes.DEFAULT_FORMAT

    def _get_grid_position(self) -> str:
        """Returns the grid position of an event."""
        start = self._get_start_grid_position()
        end = self._get_end_grid_position()
        return f'{start} / {end}'

    def _get_start_grid_position(self) -> int:
        """Returns the starting position on the grid of an event.

         The position is determined based on its start time.
         If an event is a multiday event, FIRST_GRID_BAR value is used.

        Returns:
            The position on the grid.

        """
        if self.start_multiday:
            return DivAttributes.FIRST_GRID_BAR
        return self._get_position(self.start_time)

    def _get_end_grid_position(self) -> int:
        """Returns the final position on the grid of an event.

         The position is determined based on its end time.
         If an event is a multiday event, LAST_GRID_BAR value is used.

        Returns:
            The position on the grid.

        """
        if self.end_multiday:
            return DivAttributes.LAST_GRID_BAR
        return self._get_position(self.end_time)

    @staticmethod
    def _get_position(time: datetime) -> int:
        """Returns the position on the grid of a time period.

        The grid is divided into 5 initial header sections
        and 96 quarter hour sections.

        Args:
            time: A time period.

        Returns:
            The position on the grid.

        """
        hour_position = time.hour * DivAttributes.FULL_GRID_BAR
        quarter_hour_position = DivAttributes._get_quarter_hour_position(
            time.minute)
        return (hour_position
                + quarter_hour_position
                + DivAttributes.BASE_GRID_BAR
                )

    @staticmethod
    def _get_quarter_hour_position(minutes: int) -> int:
        """Returns the quarter hour position on the grid.

        An hour is divided into 4 quarter hour (15 minutes) sections.
        The minutes are checked against the lower and upper limits
        of each section and return the correct position.

        Args:
            minutes: The minute period the event takes place.

        Returns:
            The quarter hour position on the grid.

        """
        if minutes is None:
            return DivAttributes.MIN_MINUTES

        min_minutes = DivAttributes.MIN_MINUTES
        max_minutes = DivAttributes.MAX_MINUTES
        for i in range(DivAttributes.GRID_BAR_QUARTER,
                       DivAttributes.FULL_GRID_BAR + 1):
            if min_minutes < minutes <= max_minutes:
                return i
            min_minutes = max_minutes
            max_minutes += 15
        return DivAttributes.MIN_MINUTES


@router.get('/day/{date}')
async def day_view(request: Request, date: str, db: Session = Depends(get_db)
                   ) -> Response:
    """#Returns the Day page route for a specific date.

    Args:
        request: The HTTP request.
        date: The requested date to view.
        db: Optional; The database connection.

    Returns:

    Raises:
        HTTPException:

    """
    # TODO: add a login session
    user = db.query(User).filter_by(id=get_placeholder_user().id).first()
    try:
        selected_datetime = datetime.strptime(date, '%Y-%m-%d')
    except ValueError as error:
        logger.critical(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_("Invalid date.")
        )

    day_end = selected_datetime + timedelta(hours=24)
    events = (
        db.query(Event)
        .filter(Event.owner_id == user.id)
        .filter(
            or_(
                and_(Event.start >= selected_datetime, Event.start < day_end),
                (Event.end >= selected_datetime, Event.end < day_end),
                and_(Event.start < day_end, day_end < Event.end),
            )
        )
    )
    events_n_attrs = [(event, DivAttributes(event, selected_datetime)) for
                      event in events]
    zodiac_sign = zodiac.get_zodiac_of_day(db, selected_datetime)
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events_n_attrs,
        "month": selected_datetime.strftime("%B").upper(),
        "day": selected_datetime.day,
        "zodiac": zodiac_sign,
    })
