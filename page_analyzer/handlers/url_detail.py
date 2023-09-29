import os
import psycopg2
from datetime import datetime
from flask import render_template, redirect, url_for, flash

from page_analyzer.models import Url, UrlCheck
from page_analyzer.app import app
from page_analyzer.forms import URLForm


DATABASE_URI = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(DATABASE_URI)


@app.route('/urls/<int:id>', methods=['GET', 'POST'])
def url_detail_handler(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
    row = cur.fetchone()

    if row:
        url = Url(id=row[0], name=row[1], created_at=row[2])
        form = URLForm()

        cur.execute(
            "SELECT * FROM url_checks WHERE url_id ="
            " %s ORDER BY created_at DESC", (id,))
        rows = cur.fetchall()
        checks = [UrlCheck(id=row[0], url_id=row[1], created_at=row[2],
                           h1_content=row[3], title_content=row[4],
                           description_content=row[5],
                           status_code=row[6]) for row in rows]

        cur.close()
        conn.close()

        return render_template('url.html', url=url, checks=checks,
                               form=form, datetime=datetime)
    else:
        cur.close()
        conn.close()

        flash('Страница не найдена', 'error')
        return redirect(url_for('urls_handler'))
