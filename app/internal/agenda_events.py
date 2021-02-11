from datetime import date, timedelta
from typing import Iterator, List, Optional, Union

import arrow
from sqlalchemy.orm import Session

from app.database.models import Event
from app.routers.event import sort_by_date
from app.routers.user import get_all_user_events


def get_events_per_dates(
        session: Session,
        user_id: int,
        start: date,
        end: date,
) -> Union[Iterator[Event], List]:
    """Returns a list of all the user events between the relevant dates.

    Retrieves event data from the database.

    Args:
        session: The database connection.
        user_id: The user ID of the user whose events are returned.
        start: The start of the date range.
        end: The end of the date range.

    Yields:
        An Iterator of Event objects, or an empty list
        if required parameters are not present.

    """
    if not session or not user_id or not start or not end or start > end:
        return []

    return (
        _get_filtered_events(
            sort_by_date(get_all_user_events(session, user_id)),
            start,
            end,
        )
    )


def get_event_duration(event: Event) -> Optional[str]:
    """Returns the event's duration.

    Args:
        event: An Event.

    Returns:
        The duration of the event in a string format,
        or None if no Event is passed. For
        example:

        "2 days"
        "2 days 2 hours and 30 minutes"

    """
    if not event:
        return None

    start = arrow.get(event.start)
    end = arrow.get(event.end)
    delta = event.end - event.start
    duration = end.humanize(
        start, only_distance=True, granularity=_get_delta_granularity(delta)
    )
    return duration


def _get_delta_granularity(delta: timedelta) -> List[str]:
    """Returns the delta granularity.

    Builds the granularity for the arrow module string by calculating the delta
    and returning a list of the time points: "day", "hour" and "minute".

    Args:
        delta: The timedelta between the end and starting time points.

    Returns:
        A list of the time point names.

    """
    granularity: List[str] = []

    if not delta:
        return granularity

    if delta.days > 0:
        granularity.append("day")

    hours, remainder = divmod(delta.seconds, 60 * 60)

    if hours > 0:
        granularity.append("hour")

    minutes, _ = divmod(remainder, 60)

    if minutes > 0:
        granularity.append("minute")

    return granularity


def _get_filtered_events(events: List[Event], start: date, end: date
                         ) -> Iterator[Event]:
    """Yields Events after filtering them by the requested date date.

    Yields Events which have a starting date set between the
    requested date range.

    Args:
        events: A lit of Events.
        start: The start of the date range.
        end: The end of the date range.

    Yields:
        Events which satisfy the requested date range.

    """
    yield from (
        event for event in events
        if start <= event.start.date() <= end
    )
