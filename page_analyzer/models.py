import os
import psycopg2
from datetime import datetime


DATABASE_URL = os.getenv('DATABASE_URL')


class Url:
    def __init__(self, id=None, name=None, created_at=None):
        self.id = id
        self.name = name
        self.created_at = created_at

    def __repr__(self) -> str:
        return f'<Url {self.id}>'

    @staticmethod
    def create_table():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS urls "
            "(id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, "
            "created_at TIMESTAMP NOT NULL)"
        )

        conn.commit()
        cur.close()
        conn.close()

    def save(self):
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        if self.id is None:
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) "
                "RETURNING id",
                (self.name, datetime.utcnow())
            )
            self.id = cur.fetchone()[0]
        else:
            cur.execute(
                "UPDATE urls SET name = %s, created_at = %s WHERE id = %s",
                (self.name, self.created_at, self.id)
            )

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM urls")
        rows = cur.fetchall()

        urls = [Url(id=row[0], name=row[1], created_at=row[2]) for row in rows]

        cur.close()
        conn.close()

        return urls

    @staticmethod
    def get_by_id(id):
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
        row = cur.fetchone()

        if row:
            url = Url(id=row[0], name=row[1], created_at=row[2])
        else:
            url = None

        cur.close()
        conn.close()

        return url


class UrlCheck:
    def __init__(self, id=None, url_id=None, created_at=None,
                 h1_content=None, title_content=None,
                 description_content=None, status_code=None):
        self.id = id
        self.url_id = url_id
        self.created_at = created_at
        self.h1_content = h1_content
        self.title_content = title_content
        self.description_content = description_content
        self.status_code = status_code

    def __repr__(self) -> str:
        return f'<UrlCheck {self.id}>'

    @staticmethod
    def create_table():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS url_checks "
            "(id SERIAL PRIMARY KEY, url_id INTEGER NOT NULL, "
            "created_at TIMESTAMP NOT NULL, "
            "h1_content VARCHAR(255), title_content VARCHAR(255), "
            "description_content VARCHAR(255), status_code INTEGER)"
        )

        conn.commit()
        cur.close()
        conn.close()

    def save(self):
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        if self.id is None:
            cur.execute(
                "INSERT INTO url_checks (url_id, created_at, h1_content, "
                "title_content, description_content, status_code) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (self.url_id, datetime.utcnow(), self.h1_content,
                 self.title_content, self.description_content,
                 self.status_code)
            )
            self.id = cur.fetchone()[0]
        else:
            cur.execute(
                "UPDATE url_checks "
                "SET url_id = %s, created_at = %s, h1_content = %s, "
                "title_content = %s, description_content = %s, "
                "status_code = %s WHERE id = %s",
                (self.url_id, self.created_at, self.h1_content,
                 self.title_content, self.description_content,
                 self.status_code, self.id)
            )

        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM url_checks")
        rows = cur.fetchall()

        url_checks = [UrlCheck(id=row[0], url_id=row[1],
                               created_at=row[2], h1_content=row[3],
                               title_content=row[4],
                               description_content=row[5],
                               status_code=row[6]) for row in rows]

        cur.close()
        conn.close()

        return url_checks

    @staticmethod
    def get_by_id(id):
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM url_checks WHERE id = %s", (id,))
        row = cur.fetchone()

        if row:
            url_check = UrlCheck(id=row[0], url_id=row[1],
                                 created_at=row[2], h1_content=row[3],
                                 title_content=row[4],
                                 description_content=row[5],
                                 status_code=row[6])
        else:
            url_check = None

        cur.close()
        conn.close()

        return url_check
