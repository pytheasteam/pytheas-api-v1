from .trip import Trip

from .. import db

class TripFlight(db.Model):
    __tablename__ = 'trip_flight'

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey('trips.id'),
        primary_key=True,
        nullable=False
    )

    arrival_time = db.Column(
        db.String(100),
        db.ForeignKey('hotel.id'),
        primary_key=True,
        nullable=True
    )

    departure_time = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=True
    )

    from_city = db.Column(
        db.Integer,
        db.ForeignKey('cities.id'),
        nullable=False
    )

    to_city = db.Column(
        db.Integer,
        db.ForeignKey('cities.id'),
        nullable=False
    )

    duration = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=True
    )

    price = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=False
    )

    reservation_number = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=False
    )

    trip = db.relationship(
        Trip,
        backref=db.backref("trip_flight", cascade="all, delete-orphan")
    )



