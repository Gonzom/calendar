from typing import Dict, List

from sqlalchemy.orm import Session

from app.database.models import Event, Invitation, UserEvent
from app.internal.utils import save
from app.routers.user import does_user_exist, get_users


def send_invitation(event: Event, emails: List[str], session: Session):
    """Sends invitations to all event participants.

    Args:
        event: The event the users are invited to.
        emails: A list of the event's users' emails.
        session: A database connection.

    Returns:

    """
    registered, unregistered = (
        _get_sorted_emails(emails, session=session).values()
    )

    # _send_email_invitations(unregistered, event)
    _send_in_app_invitations(registered, event, session)


def accept_invitation(invitation: Invitation, session: Session) -> None:
    """Adds a User to the Event and changes the invite status to 'accepted'.

    Accepting an invitation creates a new UserEvent entity with the User
    and the Event IDs in the database.

    The Invitation is updated with the status changed to 'accepted'.

    Args:
        invitation: The invitation sent.
        session: A database connection.
    """
    association = UserEvent(
        user_id=invitation.recipient.id,
        event_id=invitation.event.id,
    )
    invitation.status = 'accepted'
    save(session, invitation)
    save(session, association)


def _get_sorted_emails(emails: List[str], session: Session
                       ) -> Dict[str, List[str]]:
    """Returns a dictionary of emails sorted into groups.

    Args:
        emails: A list of the event's users' emails.
        session: A database connection.

    Returns:
        A dictionary of emails sorted to registered and unregistered users.

    """
    sorted_emails: Dict[str, List[str]] = {
        'registered': [],
        'unregistered': [],
    }

    for email in emails:
        if does_user_exist(email=email, session=session):
            sorted_emails['registered'].append(email)
        else:
            sorted_emails['unregistered'].append(email)
    return sorted_emails


# TODO: comment out until function is working.
# def _send_email_invitations(emails: List[str], event: Event) -> bool:
#     """Sends email invitations to unregistered users.
#
#     Args:
#         emails: A list of the event's users' emails.
#         event: The event the users are invited to.
#
#     Returns:
#
#     """
#     icalendar = event_to_icalendar(event, emails)
#     for email in emails:
#         # TODO: send email code here
#         pass
#     return True


def _send_in_app_invitations(emails: List[str], event: Event, session: Session
                             ) -> bool:
    """Sends in-app invitations for registered users.

    Args:
        emails: A list of the event's users' emails.
        event: The event the users are invited to.
        session: A database connection.

    Returns:

    """
    for email in emails:
        # An email is unique.
        user = get_users(email=email, session=session)[0]

        if user.id != event.owner.id:
            session.add(Invitation(recipient=user, event=event))

    session.commit()
    return True
