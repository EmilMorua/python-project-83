import os
from dotenv import load_dotenv
import pytest
import datetime
from bs4 import BeautifulSoup

dotenv_path = os.path.join(os.path.dirname(__file__), '.env.test')
load_dotenv(dotenv_path)

from page_analyzer.app import app as _app  # noqa
from page_analyzer.extensions import db as _db  # noqa
from page_analyzer.models import Url, UrlCheck  # noqa
from page_analyzer.handlers.add_check import (  # noqa
    create_check,
    save_check,
    get_shortened_h1_content,
    get_shortened_title_content,
    get_shortened_description_content
)


class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


# Test data for use in tests
h1 = "<html><h1>This is a long title that needs to be shortened</h1></html>"
title = ("<html><title>This is a very long page"
         " title that needs to be shortened</title></html>")
description = ("<html><meta name='description' content='This is a very "
               "long page description that needs to be shortened'></html>")
expected_value_h1 = "This is a long title that needs to be shortened"
expected_value_title = "This is a very long page title that needs to be shortened"
expected_value_description = "This is a very long page description that needs to be shortened"
text = ("<html><h1>Title</h1><title>Page Title</title><meta "
        "name='description' content='Page description'></html>")


@pytest.fixture(scope='session')
def app():
    db_uri = os.environ['SQLALCHEMY_DATABASE_URI']
    _app.config['SQLALCHEMY_TEST_DATABASE_URI'] = db_uri
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_handler(client):
    response = client.get('/')
    assert response.status_code == 200


def test_urls_handler(client, db):
    test_url = Url(name="http://example.com")
    db.session.add(test_url)
    db.session.commit()

    response = client.get('/urls')
    assert response.status_code == 200
    assert b'http://example.com' in response.data


def test_url_detail_handler(client, db):
    test_url = Url(name="http://example.com")
    db.session.add(test_url)
    db.session.commit()

    response = client.get('/urls/1')
    assert response.status_code == 200
    assert b'http://example.com' in response.data


def test_add_check_handler(db):
    new_check = UrlCheck(
        url_id=1,
        created_at=datetime.datetime.now(),
        status_code=200
    )
    db.session.add(new_check)
    db.session.commit()

    check_from_db = UrlCheck.query.filter_by(url_id=1).first()
    assert check_from_db is not None
    assert check_from_db.status_code == 200


def test_create_check():
    response = MockResponse(status_code=200, text=text)
    url_id = 1
    new_check = create_check(url_id, response)
    assert isinstance(new_check, UrlCheck)
    assert new_check.url_id == url_id
    assert new_check.h1_content == "Title"
    assert new_check.title_content == "Page Title"
    assert new_check.description_content == "Page description"


def test_save_check(db):
    test_url = Url(name="http://example.com")
    db.session.add(test_url)
    db.session.commit()

    with _app.app_context():
        url = Url.query.filter_by(name="http://example.com").first()
        assert url is not None

        new_check = UrlCheck(
            url_id=url.id,
            created_at=datetime.datetime.now(),
            status_code=200
        )
        save_check(new_check)

        saved_check = UrlCheck.query.filter_by(url_id=url.id).first()
        assert saved_check is not None
        assert saved_check.id == new_check.id
        assert saved_check.url_id == new_check.url_id
        assert saved_check.created_at == new_check.created_at
        assert saved_check.status_code == new_check.status_code
        assert saved_check.h1_content == new_check.h1_content
        assert saved_check.title_content == new_check.title_content
        assert saved_check.description_content == new_check.description_content


def test_get_shortened_h1_content():
    soup = BeautifulSoup(h1, "html.parser")
    shortened_content = get_shortened_h1_content(soup)
    assert shortened_content == expected_value_h1


def test_get_shortened_title_content():
    soup = BeautifulSoup(title, "html.parser")
    shortened_content = get_shortened_title_content(soup)
    assert shortened_content == expected_value_title


def test_get_shortened_description_content():
    soup = BeautifulSoup(description, "html.parser")
    shortened_content = get_shortened_description_content(soup)
    assert shortened_content == expected_value_description


if __name__ == "__main__":
    pytest.main()
