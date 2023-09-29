from flask_wtf.csrf import CSRFProtect
from flask import Flask
import os


app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

csrf = CSRFProtect(app)

from page_analyzer.handlers.index import index_handler  # noqa
from page_analyzer.handlers.urls import urls_handler  # noqa
from page_analyzer.handlers.url_detail import url_detail_handler  # noqa
from page_analyzer.handlers.add_check import add_check_handler  # noqa


app.route('/')(index_handler)
app.route('/urls', methods=['GET', 'POST'])(urls_handler)
app.route('/urls/<int:id>', methods=['GET', 'POST'])(url_detail_handler)
app.route('/urls/<int:id>/checks', methods=['POST'])(add_check_handler)

if __name__ == '__main__':
    app.run()
