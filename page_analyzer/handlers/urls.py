from flask import render_template, redirect, url_for, flash, request
from validators import url as validate_url
from page_analyzer.app import app

from page_analyzer.extensions import db
from page_analyzer.forms import URLForm
from page_analyzer.models import Url, UrlCheck


@app.route('/urls', methods=['GET', 'POST'])
def urls_handler():
    form = URLForm()

    if request.method == 'GET':
        urls = Url.query.order_by(Url.created_at.desc()).all()
        last_checks = get_last_checks(urls)
        return render_template(
            'urls.html',
            form=form,
            urls=urls,
            last_checks=last_checks
        )

    if request.method == 'POST':
        return handle_url_post(form)

    return render_template('urls.html', form=form)


def get_last_checks(urls: list[Url]) -> dict[int, dict[str, int]]:
    last_checks = {}
    for url in urls:
        last_check = UrlCheck.query.filter_by(url_id=url.id)\
            .order_by(UrlCheck.created_at.desc())\
            .first()
        if last_check:
            last_checks[url.id] = {
                'created_at': last_check.created_at.date(),
                'status_code': last_check.status_code
            }
    return last_checks


def handle_url_post(form: URLForm) -> str:
    url = form.url.data
    if not url:
        flash('URL обязателен', 'error')
        return redirect(url_for('index_handler'))

    if validate_url(url) and len(url) <= 255:
        existing_url = Url.query.filter_by(name=url).first()
        if existing_url:
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_detail_handler', id=existing_url.id))
    else:
        flash('Некорректный URL', 'error')
        return redirect(url_for('index_handler'))

    new_url = Url(name=url)
    db.session.add(new_url)
    db.session.commit()
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_detail_handler', id=new_url.id))
