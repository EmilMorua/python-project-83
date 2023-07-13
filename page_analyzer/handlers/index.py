from flask import render_template, redirect, url_for
from page_analyzer.forms import URLForm


def index_handler():
    form = URLForm()
    if form.validate_on_submit():
        url = form.url.data
        return redirect(url_for('urls_handler', url=url))
    return render_template('index.html', form=form)
