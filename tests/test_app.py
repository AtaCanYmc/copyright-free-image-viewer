from core.models import SearchTerm


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Copyright-free-image-viewer" in response.data


def test_setup_page(client):
    response = client.get("/setup")
    assert response.status_code == 200


def test_add_search_term(client, db_session):
    # Depending on how client/db interaction works, strictly unit testing logic might be easier
    # But let's try integration

    # Manually add to DB to verify DB works
    term = SearchTerm(term="test_term")
    db_session.add(term)
    db_session.commit()

    assert db_session.query(SearchTerm).count() == 1
