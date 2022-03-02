"""SQLAlchemy models for Flashback."""

# from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import date


bcrypt = Bcrypt()
db = SQLAlchemy()

class Song(db.Model):
    """A specific song"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Billboard data as given from API calls
    # ChartData is fetched using ChartData(name, date=None, year=None, fetch=True, timeout=25)
    # ChartData's ChartEntry instance then includes:
    # Presently, songs appear for EACH weekly billboard chart appearance. 

    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    song_img_url = db.Column(db.Text)

    # appearance = db.relationship('ChartAppearance')

#     # iTunes data / Spotify data
#     # see iTunes_Sample.json
#     # The items sync the Billboard data with iTunes. 
#     # This simplifies futher calls by skipping the search endpoint.
#     # Spotify calls are rate-limited but their data is much more expansive.

#     iTunes_artist_id = db.Column(db.Integer)
#     iTunes_collection_id = db.Column(db.Integer)
#     iTunes_track_id = db.Column(db.Integer) 
#     album = db.Column(db.text)
#     release_date = db.Column(db.DateTime)
#     genre = db.Column(db.text)

class ChartAppearance(db.Model):
    """ 
    
        Joins songs and charts.

        This is a many (songs) to many (charts) relationship.

        Each row is 1 song and the details of its chart appearance on a chart.

        Songs appear 1x for each chart appearance. 

        Charts appear once for every song they contain (e.g, 100x each). 

    """

    __tablename__ = 'appearances'

    id = db.Column(db.Integer, autoincrement=True)
    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id', ondelete='CASCADE'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id', ondelete='CASCADE'), primary_key=True)

    chart_date = db.Column(db.String, nullable=False)

    peak_pos = db.Column(db.Integer) # peak to date
    last_pos = db.Column(db.Integer)
    weeks = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    isNew = db.Column(db.Boolean)

class Chart(db.Model):
    """A specific date's chart"""

    __tablename__ = 'charts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    chart_date = db.Column(db.Date, nullable=False, unique=True)

    # appearance = db.relationship('ChartAppearance')


    @classmethod
    def next_chart(cls, get_date):

        date_as_ordinal = get_date.toordinal()

        next_chart = date_as_ordinal + 7

        return date.fromordinal(next_chart)

    @classmethod
    def prior_chart(cls, get_date):

        date_as_ordinal = get_date.toordinal()

        prior_chart = date_as_ordinal - 7

        return date.fromordinal(prior_chart)

    

class User(db.Model):
    """An application user"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    profile_img_url = db.Column(db.Text, default="/static/media/blank_profile.png")
    date_of_birth = db.Column(db.DateTime)

    # favorite_songs = db.relationship('Favorite')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    # def list_favorite_songs(self):
    #     found_song_list = [song.id for song in self.favorite_songs]
    #     return found_song_list

    @classmethod
    def signup(cls, username, password, email, profile_img_url, date_of_birth):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            profile_img_url=profile_img_url,
            date_of_birth=date_of_birth 
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

# class Favorite(db.Model):
#     """User favorites"""

#     __tablename__= 'favorites'

#     id = db.Column(db.Integer, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
#     song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)

def connect_db(app):

    db.app = app
    db.init_app(app)