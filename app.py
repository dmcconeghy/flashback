import os
import re
import billboard
import random
import requests


import datetime
from flask import Flask, render_template, redirect, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from forms import DateSearchForm, SignupForm, LoginForm
from models import db, connect_db, User, Chart, Song, ChartAppearance
from sqlalchemy import and_
from werkzeug.exceptions import Unauthorized

CURR_USER_KEY = 'current_user'
CURR_CHART = 'current_date'
uri = os.environ.get('DATABASE_URL', 'postgresql:///flashback')

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
db.create_all()

################### BEFORE (Global User) ###################

@app.before_request
def add_user_to_g():
    """ Is a user logged in? Add them to flask global g"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        
    else:
        g.user = None

################### DO LOGIN/LOGOUT ###################

def do_login(user):
    """ Log in the user"""

    session[CURR_USER_KEY] = user.id
    session.permanent = False

def do_logout():
    """ Log the user out"""

    if CURR_USER_KEY in session:
        # session.pop(CURR_USER_KEY, None)
        del session[CURR_USER_KEY]
        
################### ROOT ###################    

@app.route('/', methods=['GET', 'POST'])
def root():
    """ Returns the root / index homepage"""

    return render_template('index.html')

################### ABOUT ###################    

@app.route('/about')
def about():
    """ Returns the about page"""

    return render_template('about.html')

################### SEARCH ###################
@app.route('/exists/<string:chart_date>', methods=['GET'])
def chart_exists(chart_date):

    def previously_fetched(date_to_be_checked):
        """ 
            Does our chart date exist already? 
            Yes? Return db version.
            No? Fetch it. 
        """
        
        found_chart = (Chart
                    .query
                    .filter(Chart.chart_date == date_to_be_checked)
                    .all()) 

        if found_chart:
            return True
        else:
            return False

    if previously_fetched(chart_date):
        flash('Chart found', 'success')
        return redirect(f"/chart/{chart_date}")
        
    else:

        return redirect(f"/search/{chart_date}")
        

@app.route('/search/<string:chart_date>', methods=['GET', 'POST'])
def chart_search(chart_date):
    """ 
    Creates a chart entry and populates the db with songs and appearance data.
    """

    fetched_chart = billboard.ChartData('hot-100', date=chart_date)

    new_chart = Chart(
        name=fetched_chart.name,
        chart_date=fetched_chart.date
        # consider fetching chartData for entries?
    )

    db.session.add(new_chart)
    db.session.commit()

    for entry in fetched_chart:

        # Check if it is in our db already
        song_exists = Song.query.filter(and_(Song.title == entry.title, Song.artist == entry.artist)).first()
        
        if song_exists != [] and song_exists != None:
            
            # Check that the appearance data is different (e.g, 1990-11-11 Unchained Meloday appears twice)
            if ChartAppearance.query.filter(and_(ChartAppearance.song_id == song_exists.id, ChartAppearance.chart_date == fetched_chart.date)).first():
                new_song = Song(
                    title = entry.title, 
                    artist = entry.artist
                )

                db.session.add(new_song)
                db.session.commit()

                new_appearance = ChartAppearance(
                    chart_id = new_chart.id,
                    song_id = new_song.id,
                    peak_pos = entry.peakPos,
                    last_pos = entry.lastPos,
                    weeks = entry.weeks,
                    rank = entry.rank,
                    isNew = entry.isNew,
                    chart_date = new_chart.chart_date
                )

            else: 
                new_appearance = ChartAppearance(
                    chart_id = new_chart.id,
                    song_id = song_exists.id,
                    peak_pos = entry.peakPos,
                    last_pos = entry.lastPos,
                    weeks = entry.weeks,
                    rank = entry.rank,
                    isNew = entry.isNew,
                    chart_date = new_chart.chart_date
                )

                db.session.add(new_appearance)
                db.session.commit()

        else:
            

            new_song = Song(
                title = entry.title, 
                artist = entry.artist
            )

            db.session.add(new_song)
            db.session.commit()

            new_appearance = ChartAppearance(
                chart_id = new_chart.id,
                song_id = new_song.id,
                peak_pos = entry.peakPos,
                last_pos = entry.lastPos,
                weeks = entry.weeks,
                rank = entry.rank,
                isNew = entry.isNew,
                chart_date = new_chart.chart_date
            )

            db.session.add(new_appearance)
            db.session.commit()
    

    return redirect(f"/chart/{fetched_chart.date}")

@app.route('/search', methods=['GET', 'POST'])
def search():
    """ 
        Handles user-selected date requests.
        Passes dates to chart_search

        todo: handle date range validation

    """

    form = DateSearchForm()

    if form.validate_on_submit():
        inputted_date = form.date.data
        
        return redirect(f"/exists/{inputted_date}")
        
    return render_template("search.html", form=form)

@app.route('/random', methods=['GET', 'POST'])
def random_chart():

    earliest = datetime.date(1958, 8, 4)
    latest = datetime.date.today()
    
    random_days_between = random.randrange((latest-earliest).days)

    random_date = earliest + datetime.timedelta(days=random_days_between) 
 
    return redirect(f"/exists/{random_date}")
    
    
################### CHARTS ################### 
@app.route('/charts', methods=['GET', 'POST'])
def show_list_of_charts():
    """ This route returns a list of database stored charts """

    charts = Chart.query.all()

    return render_template('charts.html', charts=charts)

@app.route('/chart/<string:req_chart_date>', methods=['GET', 'POST'])
def show_chart(req_chart_date):
    """ 
        Display a specific chart and its songs

        This route must occur AFTER validation through exists.

        todo: fix issues with duplicate entries cf. "Unchained Melody" from 10.06.90 - 3.23.91
            There are two version on this chart but they're indistinguishable in single API data calls.
            The original peaked at #4 in 08.28.65 but *also* charted in 1990. 
            Presently, each duplicate entry adds a new Song entry, which isn't ideal. 
            There are likely many other such re-charts and duplication oddities to handle. 

    """

    chart = Chart.query.filter(Chart.chart_date == req_chart_date).first()

    appearances = (
        ChartAppearance
        .query
        .join(Song, ChartAppearance.song_id == Song.id)
        .filter(ChartAppearance.chart_date == req_chart_date)
        .order_by(ChartAppearance.rank)
        .all()
        )

    songs = (
        Song
        .query
        .join(ChartAppearance, Song.id == ChartAppearance.song_id)
        .filter(ChartAppearance.chart_date == req_chart_date)
        .all()
        )

    return render_template('chart_results.html', chart=chart, results=zip(songs, appearances))

################### SONG/S ################### 
@app.route('/songs')
def show_list_of_songs():
    """ Returns a list of database stored songs from queried charts """

    songs = Song.query.all()

    # todo: add appearances join query

    return render_template('songs.html', songs=songs)

@app.route('/song/<int:song_id>')
def show_song_details(song_id):

    song = Song.query.get_or_404(song_id)

    appearances = ChartAppearance.query.filter(ChartAppearance.song_id == song_id).all()
    print(f"BEHOLD", appearances[0].chart_date)

    return render_template('song.html', song=song, appearances=appearances)

@app.route('/songs/gallery')
def show_song_gallery():
    """ Returns a scrollable gallery of songs. """

    songs = Song.query.all()

    return render_template('song_gallery.html', songs=songs)

@app.route('/song/art/<int:song_id>', methods=['GET', 'POST'])
def fetch_song_art(song_id):
    """ 
        Fetches a specific song's album art using the iTunes API.
        This FAILS because requests executes BEFORE Song.query returns a result.  
    
    """
    song = Song.query.get_or_404(song_id)

    artist = song.artist
    title = song.title

    a = artist.replace(' ', '+')

    t = title.replace(' ', '+')


    r = requests.get('https://itunes.apple.com/search?term={{a}}&entity=musicArtist&limit=5').json()

    return render_template('fetch_art.html', song=song, a=a, r=r)

@app.route('/listing')
def listing():

    songs = Song.query.limit(20).all()

    return render_template('listing.html', songs=songs)
################### SIGNUP ###################

@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    """ Show a signup form"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    # if 'username' in session:
    #     return redirect(f"users/{session['username']}")
    
    form = SignupForm()

    if form.validate_on_submit():
       
        user = User.signup( 
            username = form.username.data, 
            password = form.password.data,
            email = form.email.data,
            profile_img_url = form.profile_img_url.data or '/static/media/blank_profile.png',
            date_of_birth = form.date_of_birth.data,
        )
       
        db.session.commit()

        flash(f"Account created! Welcome, {user.username}.", 'success')

        do_login(user)

        return redirect(f"/users/{user.id}")

    else:

        return render_template("signup.html", form=form)

################### USER ###################

@app.route('/users/<int:user_id>')
def show_user_page(user_id):
    """Show a logged in user their personal user page"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template("user_page.html", user=user)

################### LOGIN ###################

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Handle user login """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")
        
        flash("Invalid username or password", "danger")

    return render_template('login.html', form=form)

################### LOGOUT ###################

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash(f"Logged out", "success")
    
    return redirect("/login")

################### ERROR ###################

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

################### AFTER (Caching) ###################
@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
