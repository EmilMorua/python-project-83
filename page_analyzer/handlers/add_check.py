from datetime import datetime
from bs4 import BeautifulSoup
import requests
from flask import redirect, url_for, flash
from requests.exceptions import RequestException
from page_analyzer.app import app

from page_analyzer.extensions import db
from page_analyzer.models import Url, UrlCheck


@app.route('/urls/<int:id>/checks', methods=['POST'])
def add_check_handler(id):
    url = db.session.get(Url, id)
    if url:
        try:
            response = requests.get(url.name)
            new_check = create_check(url.id, response)
            save_check(new_check)
            flash('Страница успешно проверена', 'success')
        except RequestException:
            flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_detail_handler', id=id))
    else:
        flash('URL не найден', 'error')
        return redirect(url_for('urls_handler'))


def create_check(url_id: int, response: requests.Response) -> UrlCheck:
    new_check = UrlCheck(
        url_id=url_id,
        created_at=datetime.now(),
        status_code=response.status_code
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    new_check.h1_content = get_shortened_h1_content(soup)
    new_check.title_content = get_shortened_title_content(soup)
    new_check.description_content = get_shortened_description_content(soup)
    return new_check


def save_check(new_check: UrlCheck) -> None:
    db.session.add(new_check)
    db.session.commit()


def get_shortened_h1_content(soup: BeautifulSoup) -> str:
    h1_tag = soup.find('h1')
    if h1_tag:
        h1_content = h1_tag.get_text()
        if len(h1_content) > 56:
            h1_content = h1_content[:56] + '...'
        return h1_content
    return None


def get_shortened_title_content(soup: BeautifulSoup) -> str:
    title_tag = soup.find('title')
    if title_tag and title_tag.contents:
        title_content = ''.join(str(element) for element in title_tag.contents)
        title_content = title_content.strip()
        if len(title_content) > 255:
            title_content = title_content[:255] + '...'
        return title_content
    return None


def get_shortened_description_content(soup: BeautifulSoup) -> str:
    meta_attrs = {'name': 'description'}
    meta_description_tag = soup.find('meta', attrs=meta_attrs)
    if meta_description_tag:
        description_content = meta_description_tag.get('content')
        if len(description_content) > 180:
            description_content = description_content[:180] + '...'
        return description_content
    return None
