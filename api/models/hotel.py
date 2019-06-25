from .trip import Trip

from .. import db


class Hotel(db.Model):
    __tablename__ = 'hotel'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        index=False,
        unique=True,
        nullable=False
    )

    address = db.Column(
        db.String(150),
        index=False,
        unique=False,
        nullable=True
    )

    main_photo_url = db.Column(
        db.String(250),
        index=False,
        unique=False,
        nullable=True
    )

    stars = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=True
    )

    url = db.Column(
        db.String(250),
        index=False,
        unique=False,
        nullable=False
    )

    description = db.Column(
        db.String(200),
        index=False,
        unique=False,
        nullable=True
    )

    facilities = db.Column(
        db.String(45),
        index=False,
        unique=False,
        nullable=True
    )

    def __repr__(self):
        return '<Hotel {}>'.format(self.id)


class TripHotel(db.Model):
    __tablename__ = 'trip_hotel'

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey('trips.id'),
        primary_key=True,
        nullable=False
    )

    hotel_id = db.Column(
        db.Integer,
        db.ForeignKey('hotel.id'),
        primary_key=True,
        nullable=False
    )

    start_date = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=False
    )

    end_date = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=False
    )

    price_per_night = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=False
    )

    room_type = db.Column(
        db.String(100),
        index=False,
        unique=False,
        nullable=True
    )

    currency = db.Column(
        db.String(10),
        index=False,
        unique=False,
        nullable=True
    )

    trip = db.relationship(
        Trip,
        backref=db.backref("trip_hotel", cascade="all, delete-orphan")
    )

    hotel = db.relationship(
        Hotel,
        backref=db.backref("trip_hotel", cascade="all, delete-orphan")
    )


