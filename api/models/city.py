from .. import db


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        index=True,
        unique=True,
        nullable=False
    )

    country = db.Column(
        db.String(100),
        index=True,
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return '<City {}>'.format(self.name)

