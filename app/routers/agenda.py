from collections import defaultdict
from datetime import date, timedelta
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.dependencies import get_db, templates
from app.internal import agenda_events
from app.internal.utils import get_placeholder_user

router = APIRouter(
    prefix="/agenda",
    tags=["agenda"],
    responses={status.HTTP_404_NOT_FOUND: {"description": _("Not found")}},
)


def get_date_range_for_agenda(
        start: Optional[date],
        end: Optional[date],
        days: Optional[int],
) -> Tuple[date, date]:
    """Returns the start and end dates of an agenda.

    Args:
        start: Optional; The starting date of an agenda.
        end: Optional; The ending date of an agenda.
        days: Optional; The number of days the agenda spans.

    Returns:
        A tuple of the start and end dates.

    """
    if days is not None:
        start = date.today()
        end = start + timedelta(days=days)
    elif start is None or end is None:
        start = date.today()
        end = date.today()
    return start, end


@router.get("/")
def agenda(
        request: Request,
        db: Session = Depends(get_db),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: Optional[int] = None,
) -> Response:
    """Returns the Agenda page route.

    Calculates the agenda dates using the date ranges or exact amount of days.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.
        start_date: Optional; The starting date of an agenda.
        end_date: Optional; The ending date of an agenda.
        days: Optional; The number of days the agenda spans.

    Returns:
        The Agenda HTML page.

    """
    user = get_placeholder_user()  # TODO: replace with real User

    start_date, end_date = get_date_range_for_agenda(
        start_date, end_date, days
    )

    events_in_range = agenda_events.get_events_per_dates(
        db, user.id, start_date, end_date
    )

    events = defaultdict(list)
    for event in events_in_range:
        event_duration = agenda_events.get_event_duration(event)
        events[event.start.date()].append((event, event_duration))

    return templates.TemplateResponse("agenda.html", {
        "request": request,
        "events": events,
        "start_date": start_date,
        "end_date": end_date,
    })
