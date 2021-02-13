from icalendar import vCalAddress

from app.config import ICAL_VERSION, PRODUCT_ID
from app.routers import export


class TestExport:

    @staticmethod
    def test_create_icalendar():
        cal = export._create_icalendar()
        assert cal.get('version') == ICAL_VERSION
        assert cal.get('prodid') == PRODUCT_ID

    @staticmethod
    def test_create_icalendar_event(event):
        ievent = export._create_icalendar_event(event)
        assert event.owner.email in ievent.get('organizer')
        assert ievent.get('summary') == event.title

    @staticmethod
    def test_add_attendees(event):
        ievent = export._create_icalendar_event(event)
        export._add_attendees(ievent, ["test1", "test2"])
        assert len(ievent.get("attendee")) == 2

    @staticmethod
    def test_get_v_cal_address():
        email = "test_email"
        attendee = export._get_v_cal_address(email)
        test_attendee = vCalAddress(f'MAILTO:{email}')
        assert attendee == test_attendee

    @staticmethod
    def test_event_to_icalendar(user, event):
        ievent = export.event_to_icalendar(event, [user.email])

        def does_contain(item: str) -> bool:
            """Returns if calendar contains item."""
            return bytes(item, encoding='utf8') in bytes(ievent)

        assert does_contain(ICAL_VERSION)
        assert does_contain(PRODUCT_ID)
        assert does_contain(event.owner.email)
        assert does_contain(event.title)
