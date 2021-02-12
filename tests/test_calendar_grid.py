from datetime import datetime, timedelta

import pytest

import app.routers.calendar_grid as cg

DATE = datetime(1988, 5, 3)

DAY = cg.Day(datetime(1988, 5, 3))

WEEKEND = cg.DayWeekend(datetime(2021, 1, 23))

N_DAYS = 3

N_DAYS_BEFORE = datetime(1988, 4, 30)

NEXT_N_DAYS = [
    cg.Day(datetime(1988, 5, 4)),
    cg.Day(datetime(1988, 5, 5)),
    cg.Day(datetime(1988, 5, 6)),
]

WEEK_DAYS = cg.Week.WEEK_DAYS


class TestCalendarGrid:
    DATES_TO_CHECK = {
        (cg.Day, datetime(2021, 1, 20)),
        (cg.DayWeekend, datetime(2021, 1, 23)),
        (cg.Today, datetime.today().date()),
        (cg.FirstDayMonth, datetime(2021, 1, 1)),
    }

    @staticmethod
    def test_get_calendar(client):
        response = client.get("/calendar/month")
        assert response.ok
        assert b"SUNDAY" in response.content

    @staticmethod
    def test_get_calendar_extends(client):
        response = client.get(f"/calendar/month/{DAY.get_id()}")
        assert response.ok
        assert b"08" in response.content

    @staticmethod
    @pytest.mark.parametrize("day_type, date", DATES_TO_CHECK)
    def test_get_day(day_type, date):
        assert isinstance(cg.get_day(date), day_type)

    @staticmethod
    def test_get_next_date():
        next_day_generator = cg._get_next_day(DATE)
        next_day = next(next_day_generator, None)
        next_day_check = cg.Day(DATE + timedelta(days=1))
        assert next_day
        assert isinstance(next_day, cg.Day)
        assert next_day.date == next_day_check.date

    @staticmethod
    def test_get_date_before_n_days():
        assert cg.get_date_before_n_days(DATE, N_DAYS) == N_DAYS_BEFORE

    @staticmethod
    def test_get_first_day_month_block(calendar_fixture):
        first_day = next(
            calendar_fixture.itermonthdates(DATE.year, DATE.month))
        assert cg._get_first_day_month_block(DATE).date() == first_day

    @staticmethod
    def test_get_days_from_date():
        next_n_dates = cg.get_days_from_date(DATE, N_DAYS)
        for i in range(N_DAYS):
            assert next(next_n_dates).date == NEXT_N_DAYS[i].date

    @staticmethod
    def test_create_weeks():
        week = cg.get_weeks(NEXT_N_DAYS)
        assert week
        assert isinstance(week[0], cg.Week)
        assert isinstance(week[0].days[0], cg.Day)
        assert len(week) == 1 and len(week[0].days) == 3

    @staticmethod
    def test_get_month_block(calendar_fixture):
        month_weeks = cg.get_weeks(
            list(calendar_fixture.itermonthdates(1988, 5)), WEEK_DAYS)
        get_block = cg.get_month_block(cg.Day(DATE), len(month_weeks))

        for i in range(len(month_weeks)):
            for j in range(cg.Week.WEEK_DAYS):
                day = month_weeks[i].days[j]
                assert get_block[i].days[j].date.date() == day

    @staticmethod
    def test_get_user_local_time():
        time_string = "%b%w%Y"
        server_time = cg.Day.get_user_local_time()
        server_time_check = datetime.today()
        assert server_time
        assert server_time.strftime(
            time_string) == server_time_check.strftime(time_string)

    @staticmethod
    def test_is_weekend():
        assert not cg.Day.is_weekend(DATE)
        assert cg.Day.is_weekend(WEEKEND.date)

    @staticmethod
    def test_display_day():
        assert DAY.get_short_date() == '03 MAY 88'

    @staticmethod
    def test_set_id():
        assert DAY.get_id() == '03-May-1988'

    @staticmethod
    def test_display_str():
        assert str(DAY) == '03'

    @staticmethod
    def test_create_week_object():
        assert cg.Week(NEXT_N_DAYS)
