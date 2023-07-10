import pytest
from flask import url_for
from page_analyzer.app import app, db
from page_analyzer.models import Url, UrlCheck


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_index_page(client):
    with app.app_context():
        response = client.get('/')
        assert response.status_code == 200
        assert 'index.html' in response.template.name


def test_add_url_valid(client):
    with app.app_context():
        data = {'url': 'http://example.com'}
        response = client.post('/', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert 'url.html' in response.template.name
        url = Url.query.filter_by(name=data['url']).first()
        assert url is not None


def test_add_url_invalid(client):
    with app.app_context():
        data = {'url': 'invalid_url'}
        response = client.post('/', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert 'index.html' in response.template.name
        url = Url.query.filter_by(name=data['url']).first()
        assert url is None


def test_url_detail(client):
    with app.app_context():
        url = Url(name='http://example.com')
        db.session.add(url)
        db.session.commit()
        response = client.get(url_for('url_detail', id=url.id))
        assert response.status_code == 200
        assert 'url.html' in response.template.name
        assert url.name.encode() in response.data


def test_add_check(client):
    with app.app_context():
        url = Url(name='http://example.com')
        db.session.add(url)
        db.session.commit()
        response = client.post(
            url_for('add_check', id=url.id),
            follow_redirects=True)
        assert response.status_code == 200
        assert 'url.html' in response.template.name
        check = UrlCheck.query.filter_by(url_id=url.id).first()
        assert check is not None


def test_healthcheck(client):
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.data == b'OK'
