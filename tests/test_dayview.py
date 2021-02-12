from datetime import datetime, timedelta
from typing import List, Tuple

from bs4 import BeautifulSoup
import pytest

from app.database.models import Event
from app.routers.dayview import DivAttributes

EVENT_TIMES = [
    (
        datetime(year=2021, month=2, day=1, hour=13, minute=13),
        datetime(year=2021, month=2, day=1, hour=15, minute=46),
    ),
    (
        datetime(year=2021, month=2, day=3, hour=7, minute=5),
        datetime(year=2021, month=2, day=3, hour=9, minute=15),
    ),
]

MINUTES = [
    (None, 0),
    (0, 0),
    (15, 1),
    (30, 2),
    (33, 3),
    (45, 3),
    (60, 4),
]

MULTIDAY_GRID_DELTA = [
    (0, '57 / 101'),
    (24, '1 / 101'),
    (48, '1 / 57'),
]

MULTIDAY_GRID_DATE = [
    ("2021-2-1", '57 / 101'),
    ("2021-2-2", '1 / 101'),
    ("2021-2-3", '1 / 57'),
]


def get_dummy_event(start: datetime, end: datetime, user_id: int = 1) -> Event:
    """Returns an Event.

    Args:
        start: The start time of an Event.
        end: The end time of an Event.
        user_id: Optional; The ID of the user who created the Event.

    Returns:
        An Event.

    """
    return Event(title='test event',
                 content='test',
                 start=start,
                 end=end,
                 owner_id=user_id,
                 )


def get_events(dates: List[Tuple[datetime, datetime]], user_id: int
               ) -> List[Event]:
    """Returns a list of Events.

    Args:
        dates: A list of tuples of start and end dates of an Event.
        user_id: The ID of the user who created the Event.

    Returns:
        A list of Events.
    """
    events = []
    for start, end in dates:
        event = get_dummy_event(start, end, user_id)
        events.append(event)
    return events


@pytest.fixture
def event1() -> Event:
    """Returns an Event fixture."""
    start = datetime(year=2021, month=2, day=1, hour=7, minute=5)
    end = datetime(year=2021, month=2, day=1, hour=9, minute=15)
    return get_dummy_event(start, end)


@pytest.fixture
def multiday_event() -> Event:
    """Returns a multiday Event fixture."""
    start = datetime(year=2021, month=2, day=1, hour=13)
    end = datetime(year=2021, month=2, day=3, hour=13)
    return get_dummy_event(start, end)


class TestDivAttributes:

    @staticmethod
    def test_div_attributes(event1):
        div_attr = DivAttributes(event1)
        assert div_attr.total_time == '07:05 - 09:15'
        assert div_attr.grid_position == '34 / 42'
        assert div_attr.length == 130
        assert div_attr.color == 'grey'

    @staticmethod
    @pytest.mark.parametrize("minutes, result", MINUTES)
    def test_quarter_hour_position(minutes, result):
        assert DivAttributes._get_quarter_hour_position(minutes) == result

    @staticmethod
    def test_div_attributes_with_costume_color(event1):
        event1.color = 'blue'
        div_attr = DivAttributes(event1)
        assert div_attr.color == 'blue'

    @staticmethod
    @pytest.mark.parametrize("hours, grid_position", MULTIDAY_GRID_DELTA)
    def test_div_attr_multiday_grid_position(
            hours, grid_position, multiday_event):
        day = datetime(year=2021, month=2, day=1)
        day += timedelta(hours=hours)
        assert DivAttributes(multiday_event,
                             day).grid_position == grid_position


class TestDayView:

    @staticmethod
    def test_day_view_html(session, user, event1, client):
        event1.id = user.id
        events = get_events(EVENT_TIMES, user.id)
        session.add_all([event1, events[0], events[1]])
        session.commit()
        response = client.get("/day/2021-2-1")
        soup = BeautifulSoup(response.content, 'html.parser')
        assert 'FEBRUARY' in str(soup.find("div", {"id": "toptab"}))
        assert 'event1' in str(soup.find("div", {"id": "event1"}))
        assert 'event2' in str(soup.find("div", {"id": "event2"}))
        assert soup.find("div", {"id": "event3"}) is None

    @staticmethod
    @pytest.mark.parametrize("day, grid_position", MULTIDAY_GRID_DATE)
    def test_day_view_html_with_multiday_event(
            multiday_event, session, user, client, day, grid_position):
        multiday_event.id = user.id
        session.add(multiday_event)
        session.commit()
        response = client.get(f"/day/{day}")
        soup = BeautifulSoup(response.content, 'html.parser')
        grid_pos = f'grid-row: {grid_position};'
        assert grid_pos in str(soup.find("div", {"id": "event1"}))
