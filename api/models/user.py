from .. import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(80),
        index=True,
        unique=True,
        nullable=False
    )

    created = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=False
    )

    google_token = db.Column(
        db.String(150),
        index=False,
        unique=True,
        nullable=False
    )

    session_token = db.Column(
        db.String(150),
        index=False,
        unique=True,
        nullable=True
    )

    full_name = db.Column(
        db.String(100),
        index=True,
        unique=False,
        nullable=True
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)