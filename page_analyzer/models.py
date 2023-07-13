from datetime import datetime
from page_analyzer.extensions import db


class Url(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Url {self.id}>'


class UrlCheck(db.Model):
    __tablename__ = 'url_checks'

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow
    )
    h1_content = db.Column(db.String(255))
    title_content = db.Column(db.String(255))
    description_content = db.Column(db.String(255))
    status_code = db.Column(db.Integer)

    url = db.relationship('Url', backref=db.backref('checks', lazy=True))

    def __repr__(self) -> str:
        return f'<UrlCheck {self.id}>'
