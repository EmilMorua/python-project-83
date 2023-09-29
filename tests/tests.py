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
import dotenv


dotenv.load_dotenv(os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".env.test")))

app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False


print("DEBUG: DATABASE_URL =", os.getenv("DATABASE_URL"))
print("DEBUG: SECRET_KEY =", os.getenv("SECRET_KEY"))


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            Url.create_table()
            UrlCheck.create_table()
        yield client


def test_create_check():
    created_at = datetime.utcnow()
    status_code = 200
    h1_content = "Title"
    title_content = "Page Title"
    description_content = "Page description"

    url = Url(name='http://example.com')
    url.save()

    check = create_check(url.id, created_at, status_code, h1_content,
                         title_content, description_content)

    assert check is not None
    assert check.url_id == url.id
    assert check.created_at == created_at
    assert check.status_code == status_code
    assert check.h1_content == h1_content
    assert check.title_content == title_content
    assert check.description_content == description_content


def test_save_check():
    created_at = datetime.utcnow()
    status_code = 200
    h1_content = "Title"
    title_content = "Page Title"
    description_content = "Page description"

    url = Url(name='http://example.com')
    url.save()

    check = create_check(url.id, created_at, status_code, h1_content,
                         title_content, description_content)

    new_h1_content = "New Title"
    new_title_content = "New Page Title"
    new_description_content = "New Page description"

    save_check(check.id, new_h1_content, new_title_content,
               new_description_content)

    updated_check = UrlCheck.get_by_id(check.id)

    assert updated_check is not None
    assert updated_check.url_id == url.id
    assert updated_check.created_at == created_at
    assert updated_check.status_code == status_code
    assert updated_check.h1_content == new_h1_content
    assert updated_check.title_content == new_title_content
    assert updated_check.description_content == new_description_content


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
    h1 = "<html><h1>This is a long title that needs to be shortened</h1></html>"
    soup = BeautifulSoup(h1, 'html.parser')
    shortened_content = get_shortened_h1_content(soup)
    assert shortened_content == "This is a long title that needs to be shortened"


def test_get_shortened_title_content():
    title = (
        "<html><title>This is a very long page title that needs to be shortened</title></html>"
    )
    expected_value_title = "This is a very long page title that needs to be shortened"
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
        "<html><meta name='description' content='This is a very long page description that needs to be shortened'></html>"
    )
    expected_value_description = "This is a very long page description that needs to be shortened"
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
