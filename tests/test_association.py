class TestAssociation:

    @staticmethod
    def test_association_data(association, event):
        assert association.events == event

    @staticmethod
    def test_repr(association):
        assert (
                association.__repr__()
                == f'<UserEvent ({association.participants}, '
                   f'{association.events})>')
