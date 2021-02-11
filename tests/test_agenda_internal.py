from datetime import date, datetime

import pytest

from app.internal import agenda_events
from app.internal.agenda_events import get_events_per_dates


class TestAgenda:
    START = datetime(2021, 11, 1, 8, 00, 00)
    dates = [
        (
            START,
            datetime(2021, 11, 3, 8, 00),
            '2 days',
        ),
        (
            START,
            datetime(2021, 11, 3, 10, 30),
            '2 days 2 hours and 30 minutes',
        ),
        (
            START,
            datetime(2021, 11, 1, 8, 30),
            '30 minutes',
        ),
        (
            START,
            datetime(2021, 11, 1, 10, 00),
            '2 hours',
        ),
        (
            START,
            datetime(2021, 11, 1, 10, 30),
            '2 hours and 30 minutes',
        ),
        (
            START,
            datetime(2021, 11, 2, 10, 00),
            'a day and 2 hours',
        ),
    ]

    @staticmethod
    @pytest.mark.parametrize('start, end, duration', dates)
    def test_get_event_duration(event, start, end, duration):
        event.start = start
        event.end = end
        assert agenda_events.get_event_duration(event) == duration

    @staticmethod
    def test_get_events_per_dates_success(today_event, session):
        events = get_events_per_dates(
            session=session,
            user_id=today_event.owner_id,
            start=today_event.start.date(),
            end=today_event.end.date(),
        )
        assert list(events) == [today_event]

    @staticmethod
    def test_get_events_per_dates_failure(yesterday_event, session):
        events = get_events_per_dates(
            session=session,
            user_id=yesterday_event.owner_id,
            start=date.today(),
            end=date.today(),
        )
        assert list(events) == []
