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

    def __repr__(self):
        return '<Tag {}>'.format(self.name)



tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('attraction_id', db.Integer, db.ForeignKey('attractions.id'), primary_key=True)
)