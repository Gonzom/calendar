class TestHome:

    @staticmethod
    def test_home(client):
        response = client.get("/")
        assert response.ok
