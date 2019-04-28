from api.models.city import City
from api.models.trip import Trip
from .. import db


class FlightReservation(db.Model):
    __tablename__ = 'flight_reservation'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey('trips.id'),
        nullable=False
    )

    duration = db.Column(
        db.Time,
        nullable=False
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
    seat = db.Column(
        db.VARCHAR(4),
        nullable=True
    )
    flight_number = db.Column(
        db.VARCHAR(100),
        nullable=True
    )
    flight_company = db.Column(
        db.VARCHAR(100),
        nullable=False
    )

    passenger = db.Column(
        db.VARCHAR(255),
        nullable=False
    )

    date = db.Column(
        db.DATE
    )

    departure = db.Column(
        db.TIME
    )

    arrival = db.Column(
        db.TIME
    )

    gate = db.Column(
        db.VARCHAR(4)
    )

    city = db.relationship(
        City,
        backref=db.backref('cities', cascade="all, delete, delete-orphan")
    )

    trip = db.relationship(
        Trip,
        backref=db.backref('trips', cascade="all, delete, delete-orphan")
    )

    def __repr__(self):
        return '<Trip {}>'.format(self.id)
