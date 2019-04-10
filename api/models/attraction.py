from .. import db
from .tag import tags


class Attraction(db.Model):
    __tablename__ = 'attractions'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(64),
        index=True,
        unique=True,
        nullable=False
    )

    rate = db.Column(
        db.Float,
        index=True,
        unique=False,
        nullable=True
    )

    address = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=True
    )

    price = db.Column(
        db.Float,
        index=False,
        unique=False,
        nullable=True
    )

    description = db.Column(
        db.Text,
        index=False,
        unique=False,
        nullable=True
    )

    phone_number = db.Column(
        db.String(13),
        index=False,
        unique=False,
        nullable=True
    )

    website = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=True
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey('city.id'),
        nullable=False
    )
    city = db.relationship(
        'City',
        backref=db.backref('attractions', lazy=True)
    )

    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
                           backref=db.backref('attractions', lazy=True))

    def __repr__(self):
        return '<Attraction {}>'.format(self.name)






