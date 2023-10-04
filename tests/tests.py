from page_analyzer.app import app
from page_analyzer.models import Url, UrlCheck
from page_analyzer.handlers.add_check import (
    create_check,
    save_check,
    get_shortened_h1_content,
    get_shortened_title_content,
    get_shortened_description_content
)

from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from datetime import datetime
import os
import pytest
from unittest.mock import patch, MagicMock
import dotenv


dotenv.load_dotenv(os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".env.test")))

app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False


TEST_URL = 'http://example.com'
HTML_PARSER = 'html.parser'
HTML_WITH_LONG_H1 = (
    f"<html><h1>This is a long title "
    "that needs to be shortened</h1></html>"
)
EXPECTED_SHORTENED_H1 = "This is a long title that needs to be shortened"
HTML_WITH_LONG_TITLE = (
    f"<html><title>This is a very long page "
    "title that needs to be shortened</title></html>"
)
EXPECTED_SHORTENED_TITLE = (
    "This is a very long page title that needs to be shortened"
)
HTML_WITH_SHORT_TITLE = f"<html><h1>Title</h1></html>"
HTML_WITH_LONG_DESCRIPTION = (
    f"<html><meta name='description' content='This is a very"
    " long page description that needs to be shortened'></html>"
)
EXPECTED_SHORTENED_DESCRIPTION = (
    "This is a very long page description that needs to be shortened"
)
HTML_WITHOUT_META_TAG = f"<html><title>Title</title></html>"


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            Url.create_table()
            UrlCheck.create_table()
        yield client


def test_create_check():
    with patch('page_analyzer.handlers.add_check.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 4, 10, 12, 12)
    created_at = datetime(2023, 10, 4, 10, 12, 12)
    status_code = 200

    url = Url(name=TEST_URL)
    url.save()

    response = MagicMock()
    response.status_code = status_code
    response.text = ''

    check = create_check(url.id, response)
    check['created_at'] = created_at
    save_check(check)

    assert check is not None
    assert check['url_id'] == url.id
    assert str(check['created_at']) == created_at.strftime('%Y-%m-%d %H:%M:%S')


def test_save_check():
    with patch('page_analyzer.handlers.add_check.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 4, 10, 12, 12)
    created_at = datetime(2023, 10, 4, 10, 12, 12)
    status_code = 200

    url = Url(name=TEST_URL)
    url.save()

    response = MagicMock()
    response.status_code = status_code
    response.text = ''

    check = create_check(url.id, response)
    check['created_at'] = created_at
    save_check(check)

    with patch('page_analyzer.models.UrlCheck.get_by_id', return_value=check):
        updated_check = UrlCheck.get_by_id(check['url_id'])

    assert updated_check is not None
    assert updated_check['url_id'] == url.id
    assert str(updated_check['created_at']
               ) == created_at.strftime('%Y-%m-%d %H:%M:%S')


def test_add_check_handler_request_exception(client, mocker):
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = RequestException()

    url = Url(name=TEST_URL)
    url.save()

    response = client.post(f'/urls/{url.id}/checks')
    assert response.status_code == 302
    assert "Произошла ошибка при проверке" not in response.get_data(
        as_text=True)
    assert response.location.endswith(f"/urls/{url.id}")


def test_get_shortened_h1_content():
    soup = BeautifulSoup(HTML_WITH_LONG_H1, HTML_PARSER)
    shortened_content = get_shortened_h1_content(soup)
    assert shortened_content == EXPECTED_SHORTENED_H1


def test_get_shortened_title_content():
    soup = BeautifulSoup(HTML_WITH_LONG_TITLE, HTML_PARSER)
    shortened_content = get_shortened_title_content(soup)
    assert shortened_content == EXPECTED_SHORTENED_TITLE


def test_get_shortened_title_content_no_title_tag():
    soup = BeautifulSoup(HTML_WITH_SHORT_TITLE, HTML_PARSER)
    shortened_content = get_shortened_title_content(soup)
    assert shortened_content is None


def test_get_shortened_description_content():
    soup = BeautifulSoup(HTML_WITH_LONG_DESCRIPTION, HTML_PARSER)
    shortened_content = get_shortened_description_content(soup)
    assert shortened_content == EXPECTED_SHORTENED_DESCRIPTION


def test_get_shortened_description_content_no_meta_tag():
    soup = BeautifulSoup(HTML_WITHOUT_META_TAG, HTML_PARSER)
    shortened_content = get_shortened_description_content(soup)
    assert shortened_content is None


if __name__ == '__main__':
    pytest.main()
