from .. import db


class UserProfile(db.Model):
    from api.models.user import User

    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )
    name = db.Column(
        db.String(50)
    )
    image = db.Column(
        db.String(250)
    )

    user = db.relationship(User, backref=db.backref("user_profile", cascade="all, delete-orphan"))

    def __repr__(self):
        return '<Use - Profile {} - {}>'.format(self.user_id, self.name)


class ProfileTag(db.Model):
    from .tag import Tag

    __tablename__ = 'profile_tag'

    id = db.Column(db.Integer, primary_key=True)

    profile_id = db.Column(
        db.Integer,
        db.ForeignKey('user_profile.id')
    )

    tag_id = db.Column(
        db.Integer,
        db.ForeignKey('tag.id')
    )

    profile = db.relationship(UserProfile, backref=db.backref("profile_tag", cascade="all, delete, delete-orphan"))
    tag = db.relationship(Tag, backref=db.backref("profile_tag", cascade="all, delete, delete-orphan"))


