"""SQLAlchemy models for Flashback."""

# from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):

    db.app = app
    db.init_app(app)

class Song(db.Model):
    """A specific song"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Billboard data as given from API calls
    # ChartData is fetched using ChartData(name, date=None, year=None, fetch=True, timeout=25)
    # ChartData's ChartEntry instance then includes:

    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    song_img_url = db.Column(db.Text)
    peak_pos = db.Column(db.Integer)
    last_pos = db.Column(db.Integer)
    weeks = db.Column(db.Integer)
    rank = db.Column(db.Integer, nullable=False)
    isNew = db.Column(db.Boolean)

    # iTunes data / Spotify data
    # see iTunes_Sample.json
    # The items sync the Billboard data with iTunes. 
    # This simplifies futher calls by skipping the search endpoint.
    # Spotify calls are rate-limited but their data is much more expansive.

    iTunes_artist_id = db.Column(db.Integer)
    iTunes_collection_id = db.Column(db.Integer)
    iTunes_track_id = db.Column(db.Integer) 
    album = db.Column(db.text)
    release_date = db.Column(db.DateTime)
    genre = db.Column(db.text)

    charts = db.relationship('Chart')

class User(db.Model):
    """An application user"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(Min=6, Max=20), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    profile_img_url = db.Column(db.Text, default="/static/images/default-pic.png" )
    date_of_birth = db.Column(db.DateTime)

    favorite_songs = db.relationship('Favorite')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def list_favorite_songs(self):
        found_song_list = [song.id for song in self.favorite_songs]
        return found_song_list

    # @classmethod
    # def signup(cls, username, email, password):
    #     """Sign up user.

    #     Hashes password and adds user to system.
    #     """

    #     hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

    #     user = User(
    #         username=username,
    #         email=email,
    #         password=hashed_pwd
    #     )

    #     db.session.add(user)
    #     return user

    # @classmethod
    # def authenticate(cls, username, password):
    #     """Find user with `username` and `password`.

    #     This is a class method (call it on the class, not an individual user.)
    #     It searches for a user whose password hash matches this password
    #     and, if it finds such a user, returns that user object.
    #     If can't find matching user (or if password is wrong), returns False.
    #     """

    #     user = cls.query.filter_by(username=username).first()

    #     if user:S
    #         is_auth = bcrypt.check_password_hash(user.password, password)
    #         if is_auth:
    #             return user

    #     return False

class Chart(db.Model):
    """A specific date's chart"""

    __tablename__ = 'charts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    songs = db.relationship('Song')

class Favorite(db.Model):
    """User favorites"""

    __tablename__= 'favorites'

    id = db.Column(db.Integer, autoincrement=True)
    user_id = db.Column(db.Integer, db.Foreignkey('users.id', ondelete='cascade'), primary_key=True)
    song_id = db.Column(db.Integer, db.Foreignkey('songs.id'), primary_key=True)

class ChartedSongs(db.Model):
    """Joins a chart with its songs"""

    __tablename__ = 'chartedsongs'

    id = db.Column(db.Integer, autoincrement=True)
    chart_id = db.Column(db.Integer, db.Foreignkey('charts.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.Foreignkey('songs.id'), primary_key=True)