from app.routers import share
from app.routers.invitation import get_all_invitations


class TestShareEvent:

    @staticmethod
    def test_share_success(user, event, session):
        emails = [user.email]
        share.send_invitation(event, emails, session)
        invitations = get_all_invitations(db=session, recipient_id=user.id)
        assert invitations != []

    @staticmethod
    def test_share_failure(event, session):
        emails = [event.owner.email]
        share.send_invitation(event, emails, session)
        invitations = get_all_invitations(
            db=session, recipient_id=event.owner.id)
        assert invitations == []

    @staticmethod
    def test_sort_emails(user, session):
        # The user is being imported, so they will be created.
        data = [
            'test.email@gmail.com',  # registered user
            'not_logged_in@gmail.com',  # unregistered user
        ]
        sorted_emails = share._get_sorted_emails(data, session=session)
        assert sorted_emails == {
            'registered': ['test.email@gmail.com'],
            'unregistered': ['not_logged_in@gmail.com'],
        }

    @staticmethod
    def test_send_in_app_invitations(user, sender, event, session):
        assert share._send_in_app_invitations(
            [user.email], event, session=session)
        invitation = get_all_invitations(db=session, recipient=user)[0]
        assert invitation.event.owner == sender
        assert invitation.recipient == user
        session.delete(invitation)

    @staticmethod
    def test_send_in_app_invitation_failure(user, sender, event, session):
        assert share._send_in_app_invitations(
            [user.email, sender.email], event, session=session)
        invitations = get_all_invitations(db=session, recipient=user)
        assert len(invitations) == 1
        invitation = invitations[0]
        assert invitation.event.owner == sender
        assert invitation.recipient == user
        session.delete(invitation)

    # TODO add email tests when function is completed.
    # @staticmethod
    # def test_send_email_invitations(user, event):
    #     share._send_email_invitations([user.email], event)
    #
    #     assert True

    @staticmethod
    def test_accept(invitation, session):
        share.accept_invitation(invitation, session=session)
        assert invitation.status == 'accepted'
