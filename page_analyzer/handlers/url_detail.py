from flask import render_template, redirect, url_for, flash
from page_analyzer.models import Url, UrlCheck
from page_analyzer.app import app
from page_analyzer.forms import URLForm


@app.route('/urls/<int:id>', methods=['GET', 'POST'])
def url_detail_handler(id):
    url = Url.query.get(id)
    if url:
        form = URLForm()
        checks = UrlCheck.query \
            .filter_by(url_id=id) \
            .order_by(UrlCheck.created_at.desc()) \
            .all()
        return render_template('url.html', url=url, checks=checks, form=form)
    else:
        flash('Страница не найдена', 'error')
        return redirect(url_for('urls_handler'))
