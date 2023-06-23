from app import db


class Url(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, name):
        self.name = name


class UrlCheck(db.Model):
    __tablename__ = 'url_checks'

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'))
    status_code = db.Column(db.Integer)
    h1 = db.Column(db.String(255))
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, url_id, created_at):
        self.url_id = url_id
        self.created_at = created_at
