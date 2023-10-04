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

    url = Url(name='http://example.com')
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

    url = Url(name='http://example.com')
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

    url = Url(name='http://example.com')
    url.save()

    response = client.post(f'/urls/{url.id}/checks')
    assert response.status_code == 302
    assert "Произошла ошибка при проверке" not in response.get_data(
        as_text=True)
    assert response.location.endswith(f"/urls/{url.id}")


def test_get_shortened_h1_content():
    h1 = ("<html><h1>This is a long title "
          "that needs to be shortened</h1></html>")
    soup = BeautifulSoup(h1, 'html.parser')
    shortened_content = get_shortened_h1_content(soup)
    assert shortened_content == ("This is a long title"
                                 " that needs to be shortened")


def test_get_shortened_title_content():
    title = (
        "<html><title>This is a very long page "
        "title that needs to be shortened</title></html>")
    expected_value_title = ("This is a very long page "
                            "title that needs to be shortened")
    soup = BeautifulSoup(title, "html.parser")
    shortened_content = get_shortened_title_content(soup)
    assert shortened_content == expected_value_title


def test_get_shortened_title_content_no_title_tag():
    no_title_tag = "<html><h1>Title</h1></html>"
    soup = BeautifulSoup(no_title_tag, "html.parser")
    shortened_content = get_shortened_title_content(soup)
    assert shortened_content is None


def test_get_shortened_description_content():
    description = (
        "<html><meta name='description' content='This is a very"
        " long page description that needs to be shortened'></html>")
    expected_value_description = ("This is a very long page "
                                  "description that needs to be shortened")
    soup = BeautifulSoup(description, "html.parser")
    shortened_content = get_shortened_description_content(soup)
    assert shortened_content == expected_value_description


def test_get_shortened_description_content_no_meta_tag():
    no_meta_tag = "<html><title>Title</title></html>"
    soup = BeautifulSoup(no_meta_tag, "html.parser")
    shortened_content = get_shortened_description_content(soup)
    assert shortened_content is None


if __name__ == '__main__':
    pytest.main()
