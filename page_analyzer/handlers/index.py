from flask import render_template, redirect, url_for, request
from page_analyzer.forms import URLForm


def index_handler():
    form = URLForm()
    if request.method == 'POST':
        url = request.form['url']
        return redirect(url_for('urls_handler', url=url))
    return render_template('index.html', form=form)
