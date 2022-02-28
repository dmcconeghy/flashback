
import os
import billboard
from datetime import date, timedelta
import random
import requests
from dbsecrets import DB_SECRET_KEY

from flask import Flask, render_template, redirect, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import DateSearchForm, SignupForm, LoginForm
from models import db, connect_db, User, Chart, Song

from werkzeug.exceptions import Unauthorized

CURR_USER_KEY = 'current_user'
CURR_CHART = 'current_date'

app = Flask(__name__)

if os.environ.get('MODE') == 'PRODUCTION':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)   
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///flashback')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')
toolbar = DebugToolbarExtension(app)

connect_db(app)
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

@app.route('/search/<string:chart_date>', methods=['GET', 'POST'])
def chart_search(chart_date):
    """ Searches for a chart in the database by date"""

    chart_exists = Chart.query.filter(Chart.chart_date == chart_date).all()

    # Chart isn't in the database
    if chart_exists == []:

        fetched_chart = billboard.ChartData('hot-100', date=chart_date)

        new_chart = Chart(
            name=fetched_chart.name,
            chart_date=fetched_chart.date
        )

        db.session.add(new_chart)
        
        for entry in fetched_chart:

            new_song = Song(
                title = entry.title,
                artist = entry.artist,
                peak_pos = entry.peakPos,
                last_pos = entry.lastPos,
                weeks = entry.weeks,
                rank = entry.rank,
                isNew = entry.isNew,
                chart_date = new_chart.chart_date
            )

            db.session.add(new_song)

        db.session.commit()

        return render_template('results.html', chart=fetched_chart)

    else:
        flash('Chart already in database', 'success')
        return redirect('/charts')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """ 
        Handles user-selected date requests.
        Passes dates to chart_search

        TODO: handle date range validation

    """

    form = DateSearchForm()

    if form.validate_on_submit():
        inputted_date = form.date.data

        return redirect(f"/search/{inputted_date}")

    return render_template("search.html", form=form)

@app.route('/random', methods=['GET', 'POST'])
def random_chart():

    earliest = date(1958, 8, 4)
    latest = date.today()
    
    random_days_between = random.randrange((latest-earliest).days)

    random_date = earliest + timedelta(days=random_days_between)

    return redirect(f"/search/{random_date}")

################### CHARTS ################### 
@app.route('/charts', methods=['GET', 'POST'])
def show_list_of_charts():
    """ This route returns a list of database stored charts """

    charts = Chart.query.all()

    return render_template('charts.html', charts=charts)

@app.route('/chart/<string:req_chart_date>')
def show_chart(req_chart_date):
    """ 
        Display a specific chart and its songs
    """

    chart_exists = Chart.query.filter(Chart.chart_date == req_chart_date).limit(1).all()

    if chart_exists != []:
        # Limit to 1 until bug with multiple version of chart is fixed.
        charts = chart_exists 
    else:    
        charts = Chart.query.filter(Chart.chart_date == req_chart_date).limit(1).all()

    songs = Song.query.filter(Song.chart_date == req_chart_date).order_by(Song.rank.asc()).all()

    print(charts, chart_exists)
    return render_template('chart_results.html', charts=charts, songs=songs)

################### SONG/S ################### 
@app.route('/songs')
def show_list_of_songs():
    """ Returns a list of database stored songs from queried charts """

    songs = Song.query.all()

    return render_template('songs.html', songs=songs)

@app.route('/song/<int:song_id>')
def show_song_details(song_id):

    song = Song.query.get_or_404(song_id)

    return render_template('song.html', song=song)

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
