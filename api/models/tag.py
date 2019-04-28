from .. import db


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        index=True,
        unique=True,
        nullable=False
    )

    attraction = db.relationship('Attraction', secondary='attractions_tags')

    def __repr__(self):
        return '<Tag {}>'.format(self.name)

