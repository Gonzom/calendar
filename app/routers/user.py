from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Event, User, UserEvent
from app.internal.utils import save


def create_user(
        username: str,
        password: str,
        email: str,
        language_id: int,
        session: Session,
) -> User:
    """Returns a User object after saving it to the database.

    Args:
        username: The user's username.
        password: The user's password.
        email: The user's email.
        language_id: The language ID for the user's language setting.
        session: The database connection.

    Returns:
        A new User object.

    """
    user = User(
        username=username,
        password=password,
        email=email,
        language_id=language_id,
    )
    save(session, user)
    return user


def get_users(session: Session, **param) -> List[User]:
    """Returns all users filtered by the requested parameters.

    Args:
        session: The database connection.
        **param: A list of parameters to filter the results.

    Returns:
        A list of Users satisfying the criteria.
    """
    try:
        users = list(session.query(User).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return users


def does_user_exist(
        session: Session,
        *,
        user_id=None,
        username=None,
        email=None,
) -> bool:
    """Returns True if User exists in database.

    A user can be searched by one of three unique parameters:
    ID, username and email.

    Args:
        session: The database connection.
        user_id: The user's ID.
        username: The user's username.
        email: The user's email.

    Returns:
        Returns True if User exists, otherwise returns False
    """
    if user_id:
        return len(get_users(session=session, id=user_id)) == 1

    if username:
        return len(get_users(session=session, username=username)) == 1

    if email:
        return len(get_users(session=session, email=email)) == 1

    return False


def get_all_user_events(session: Session, user_id: int) -> List[Event]:
    """Returns all events that the user participants in."""

    return (session.query(Event)
            .join(UserEvent)
            .filter(UserEvent.user_id == user_id)
            .all()
            )
