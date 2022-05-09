"""SQLAlchemy models for Flashback."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from dateutil.relativedelta import relativedelta


bcrypt = Bcrypt()
db = SQLAlchemy()

class Song(db.Model):
    """A specific song"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Billboard data as given from API calls to billboard.py
    # ChartData is fetched using ChartData(name, date=None, year=None, fetch=True, timeout=25)
    # images endpoint does not work and is instantiated with a default art image. 
    
    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    song_img_url = db.Column(db.Text, default='../static/media/missing_album_art.svg')
    charts = db.relationship('ChartAppearance')
    favorite = db.relationship('Favorite')


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
    """
    
        A specific date's chart. Charts have names and dates and a relationship to their songs. 

        Methods include next/prior chart options for easy access in html pagination.
        
        
    """

    __tablename__ = 'charts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    chart_date = db.Column(db.Date, nullable=False, unique=True)

    songs = db.relationship('ChartAppearance')

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
    """
        An application user. 
        Includes methods for returning birthday charts, 
        signing up as a new user, and authenticating an existing user. 
    
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.Text, nullable=True)
    profile_img_url = db.Column(db.Text, default="/static/media/blank_profile.png")
    date_of_birth = db.Column(db.Date)

    favorite_songs = db.relationship('Favorite', cascade='all, delete', passive_deletes=True)

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def birth_charts(self, age):
        """
            Given a user's birthday and an age input, returns the date for that age.
        """
        # birthday_ordinal = self.date_of_birth.toordinal()

        # age_ordinal = age * 365.25

        chart_at_age = self.date_of_birth + relativedelta(years=age)

        if chart_at_age > date.today():
            chart_at_age = date.today()

        return chart_at_age



    @classmethod
    def signup(cls, username, password, email, profile_img_url, date_of_birth):
        """
            Sign up user.
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
        """
            Find user with `username` and `password`.

            This is a class/static method 
            It searches for a user whose password hash matches this password
            and, if it finds such a user, returns that user object.
            If it can't find matching user (or if password is wrong), returns False.

        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Favorite(db.Model):
    """
        User favorites. Intersection of a user and a song key with single reference id. 
    
    """

    __tablename__= 'favorites'

    id = db.Column(db.Integer, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)


def connect_db(app):

    db.app = app
    db.init_app(app)