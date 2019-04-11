from api import db


class TagAttraction(db.Model):
    from api.models.attraction import Attraction
    from api.models.tag import Tag

    __tablename__ = 'attractions_tags'

    tag_id = db.Column(
        db.Integer,
        db.ForeignKey('tag.id'),
        primary_key=True
    )
    attraction_id = db.Column(
        db.Integer,
        db.ForeignKey('attractions.id'),
        primary_key=True
    )

    attraction = db.relationship(Attraction, backref=db.backref("attractions_tags", cascade="all, delete-orphan"))
    tag = db.relationship(Tag, backref=db.backref("attractions_tags", cascade="all, delete-orphan"))

    def __repr__(self):
        return '<Tag - Attraction {} - {}>'.format(self.tag_id, self.attraction_id)