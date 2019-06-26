from .attraction import Attraction
from .city import City
from .user import User
from .user_trip_profile import UserProfile

from .. import db


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    profile_id = db.Column(
        db.Integer,
        db.ForeignKey('user_profile.id'),
        nullable=False
    )

    currency = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=True
    )

    price = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=True
    )

    days = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=True
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey('cities.id'),
        nullable=False
    )

    start_date = db.Column(
        db.Date,
        index=False,
        unique=False,
        nullable=True
    )

    end_date = db.Column(
        db.Date,
        index=False,
        unique=False,
        nullable=True
    )

    is_booked = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=False
    )

    people_number = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False
    )

    hotel_rsrv_code = db.Column(
        db.String(100),
        nullable=True
    )

    city = db.relationship(
        City,
        backref=db.backref('trips', cascade="all, delete, delete-orphan")
    )

    user = db.relationship(
        User,
        backref=db.backref('trips', cascade="all, delete, delete-orphan")
    )

    profile = db.relationship(
        UserProfile,
        backref=db.backref('trips', cascade="all, delete, delete-orphan")
    )

    def __repr__(self):
        return '<Trip {}>'.format(self.id)


class TripAttraction(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey('trips.id'),
        nullable=False
    )
    attraction_id = db.Column(
        db.Integer,
        db.ForeignKey('attractions.id'),
        nullable=False
    )
    day = db.Column(
        db.Integer,
        nullable=False
    )

    trip = db.relationship(
        Trip,
        backref=db.backref("trip_attraction", cascade="all, delete-orphan")
    )

    attraction = db.relationship(
        Attraction,
        backref=db.backref("trip_attraction", cascade="all, delete-orphan")
    )


