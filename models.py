"""SQLAlchemy models for Flashback."""

# from datetime import datetime

from bs4 import BeautifulSoup
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from dateutil.relativedelta import relativedelta
import requests

bcrypt = Bcrypt()
db = SQLAlchemy()

class Song(db.Model):
    """A specific song"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Billboard data as given from API calls to billboard.py
    # ChartData is fetched using ChartData(name, date=None, year=None, fetch=True, timeout=25)
    
    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    song_img_url = db.Column(db.Text, default='../static/media/missing_album_art.svg')
    artist_page = db.Column(db.Text, default="Not Queried")
    missing_image = db.Column(db.Boolean, default=None)
    missing_page = db.Column(db.Boolean, default=None)

    charts = db.relationship('ChartAppearance')
    favorite = db.relationship('Favorite')

    def has_image(self):

        if self.missing_image == True:
            return False
        elif self.missing_image == False:
            return True
        else:
            return None
       
    def find_artist_page(self):

        hyphen_artist = self.artist.replace(' ', '-').lower()
        formatted_url = f"http://billboard.com/artist/{hyphen_artist}"

        r = requests.get(formatted_url)

        if r.status_code != 404:

            self.artist_page = formatted_url
            self.missing_page = False
            db.session.commit()
        
        else: 
            print("Artist Page doesn't exist")
            self.missing_page = True
            db.session.commit()
            return False

    def get_artist_image(self):

        # Only search if the artist page hasn't been queried
        if self.artist_page != "Not Queried":
            response_data = requests.get(self.artist_page).text
            
            soup = BeautifulSoup(response_data, 'html.parser')
            alt = f"An image of {self.artist}"
            print(alt)
            img_element = soup.find('img', alt=alt)
            print(img_element)

            lazy_load = 'https://www.billboard.com/wp-content/themes/vip/pmc-billboard-2021/assets/public/lazyload-fallback.gif'

            if img_element != None:
                
                if img_element['data-lazy-src'] != None and img_element['data-lazy-src'] != lazy_load:
                    self.song_img_url = img_element['data-lazy-src']
                    self.missing_image = False
                elif img_element['src'] != lazy_load and img_element['src'] != None:
                    self.song_img_url = img_element['src']
                    self.missing_image = False  
                
            else:
                self.missing_image = True 
                return print("Artist Image Not Found")
        db.session.commit()

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
    """An application user"""

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

class Favorite(db.Model):
    """User favorites"""

    __tablename__= 'favorites'

    id = db.Column(db.Integer, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)


def connect_db(app):

    db.app = app
    db.init_app(app)