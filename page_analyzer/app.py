from datetime import datetime

import os
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash
from validators import url as validate_url

from page_analyzer.extensions import db
from page_analyzer.forms import URLForm
from page_analyzer.models import Url, UrlCheck


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    if form.validate_on_submit():
        url = form.url.data
        if validate_url(url) and len(url) <= 255:
            new_url = Url(name=url)
            db.session.add(new_url)
            db.session.commit()
            flash('URL успешно добавлен', 'success')
            return redirect(url_for('url_detail', id=new_url.id))
        else:
            flash('Ошибка: некорректный URL', 'error')

    return render_template('index.html', form=form)


@app.route('/urls')
def urls():
    urls = Url.query.order_by(Url.created_at.desc()).all()
    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def create_url():
    form = URLForm()
    if form.validate_on_submit():
        url = form.url.data
        if validate_url(url) and len(url) <= 255:
            new_url = Url(name=url)
            db.session.add(new_url)
            db.session.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_detail', id=new_url.id))
        else:
            flash('Ошибка: некорректный URL', 'error')
    return redirect(url_for('index'))


@app.route('/urls/<int:id>')
def url_detail(id):
    url = Url.query.get(id)
    if url:
        checks = UrlCheck.query.filter_by(url_id=id).order_by(
            UrlCheck.created_at.desc()).all()
        return render_template('url.html', url=url, checks=checks)
    else:
        flash('Страница не найдена', 'error')
        return redirect(url_for('urls'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def add_check(id):
    url = Url.query.get(id)
    if url:
        new_check = UrlCheck(url_id=id, created_at=datetime.now())
        db.session.add(new_check)
        db.session.commit()

        response = requests.get(url.name)
        soup = BeautifulSoup(response.text, 'html.parser')

        h1_tag = soup.find('h1')
        if h1_tag:
            new_check.h1_content = h1_tag.get_text()

        title_tag = soup.find('title')
        if title_tag:
            new_check.title_content = title_tag.get_text()

        meta_description_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_description_tag:
            new_check.description_content = meta_description_tag.get('content')

        db.session.add(new_check)
        db.session.commit()

        flash('Проверка успешно добавлена', 'success')
        return redirect(url_for('url_detail', id=id))
    else:
        flash('URL не найден', 'error')
        return redirect(url_for('urls'))


@app.route('/healthcheck')
def healthcheck():
    return "OK"


if __name__ == '__main__':
    app.run()
