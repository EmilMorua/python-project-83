from flask import render_template, redirect, url_for, flash, request
from validators import url as validate_url
import psycopg2
import os
from datetime import datetime

from page_analyzer.app import app
from page_analyzer.models import Url


DATABASE_URL = os.getenv('DATABASE_URL')


def get_last_checks(urls):
    last_checks = {}
    with app.app_context():
        connection = psycopg2.connect(DATABASE_URL)
        cur = connection.cursor()
        for url in urls:
            cur.execute(
                "SELECT created_at, status_code FROM url_checks "
                "WHERE url_id = %s "
                "ORDER BY created_at DESC "
                "LIMIT 1",
                (url.id,)
            )
            row = cur.fetchone()
            if row:
                last_checks[url.id] = {
                    'created_at': row[0].strftime('%Y-%m-%d'),
                    'status_code': row[1]
                }
        cur.close()
        connection.close()
    return last_checks


def is_valid_url(url):
    return bool(url) and validate_url(url) and len(url) <= 255


def find_existing_url_id(url, connection):
    with connection.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
        existing_url = cur.fetchone()
        return existing_url[0] if existing_url else None


def add_new_url_to_database(url, connection):
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s) "
            "RETURNING id",
            (url, datetime.utcnow())
        )
        return cur.fetchone()[0]


def handle_url_post(form):
    url = form['url']

    if not is_valid_url(url):
        flash('Некорректный URL', 'error')
        return redirect(url_for('index_handler'))

    with app.app_context():
        connection = psycopg2.connect(DATABASE_URL)
        try:
            existing_url_id = find_existing_url_id(url, connection)
            if existing_url_id:
                flash('Страница уже существует', 'info')
                return redirect(url_for('url_detail_handler',
                                        id=existing_url_id))

            new_url_id = add_new_url_to_database(url, connection)
            connection.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_detail_handler', id=new_url_id))
        finally:
            connection.close()


@app.route('/urls', methods=['GET', 'POST'])
def urls_handler():
    form = request.form

    if request.method == 'GET':
        with app.app_context():
            connection = psycopg2.connect(DATABASE_URL)
            cur = connection.cursor()
            cur.execute("SELECT * FROM urls ORDER BY created_at DESC")
            urls_data = cur.fetchall()
            urls = [Url(id=row[0], name=row[1], created_at=row[2])
                    for row in urls_data]
            cur.close()
            connection.close()
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
