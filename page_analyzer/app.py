from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from validators import url as validate_url
from datetime import datetime
from page_analyzer.forms import URLForm
import os


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

from page_analyzer.models import Url, UrlCheck


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


@app.route('/urls/<int:id>')
def url_detail(id):
    url = Url.query.get(id)
    if url:
        return render_template('url.html', url=url)
    else:
        flash('URL не найден', 'error')
        return redirect(url_for('urls'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def add_check(id):
    url = Url.query.get(id)
    if url:
        new_check = UrlCheck(url_id=id, created_at=datetime.now())
        db.session.add(new_check)
        db.session.commit()
        flash('Проверка успешно добавлена', 'success')
        return redirect(url_for('url_detail', id=id))
    else:
        flash('URL не найден', 'error')
        return redirect(url_for('urls'))


def get_last_checks():
    last_checks = {}
    checks = UrlCheck.query.order_by(UrlCheck.created_at.desc()).all()
    for check in checks:
        if check.url_id not in last_checks:
            last_checks[check.url_id] = check.created_at
    return last_checks


@app.route('/healthcheck')
def healthcheck():
    return "OK"


if __name__ == '__main__':
    app.run()
