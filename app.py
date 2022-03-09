from ctypes import util
import os
import requests

from flask import Flask, render_template, redirect, session, flash, g 
from flask_debugtoolbar import DebugToolbarExtension


from werkzeug.exceptions import Unauthorized

from models import db, connect_db, User, Song, Favorite
from forms import SignupForm, LoginForm, NewSongForFavoriteList
import chart
import song
import search
import utilities


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

################### USER SIGNUP ###################

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

################### USER PROFILE PAGE ###################

@app.route('/users/<int:user_id>')
def show_user_page(user_id):
    """Show a logged in user their personal user page"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template("user_page.html", user=user)

################### USER LOGIN ###################

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

################### USER LOGOUT ###################

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash(f"Logged out", "success")
    
    return redirect("/login")

################### CHARTS ################### 
#
#   See charts.py for:
# 
#   def show_chart(req_chart_date) for a specific date's chart
#   def show_list_of_charts() for all charts in the database   
#
app.add_url_rule('/charts', view_func=chart.show_list_of_charts, methods=['GET', 'POST'])
app.add_url_rule('/chart/<string:req_chart_date>', view_func=chart.show_chart, methods=['GET', 'POST'])

################### SONG/S ################### 
#
#   See song.py for
#  
#   def show_list_of_songs(page=1) for a paginated list of songs in the database
#   def show_song_details(song_id) for a detailed song page
#   def show_song_gallery() for a gallery version of a selection of songs in the database
#   def fetch_song_art(song_id) for querying a song's art. Should be admin-only. 
#   def listing() for a jukebox style version of chart information
# 
app.add_url_rule('/songs', view_func=song.show_list_of_songs, methods=['GET', 'POST'])
app.add_url_rule('/songs/<int:page>', view_func=song.show_list_of_songs, methods=['GET', 'POST'])
app.add_url_rule('/song/<int:song_id>', view_func=song.show_song_details)
app.add_url_rule('/songs/gallery', view_func=song.show_song_gallery)
app.add_url_rule('/song/art/<int:song_id>', view_func=song.fetch_song_art, methods=['GET', 'POST'])
app.add_url_rule('/listing', view_func=song.listing)

################### SEARCH ###################
# 
#   See search.py for
# 
#   def chart_exists(chart_date) a helper route to prevent uncessessary API calls.
#   def chart_search(chart_date) the interface between the API and database inputs
#   def search() the request page for a specific or random chart.
#   def random_chart() returns a random chart date.
# 
app.add_url_rule('/exists/<string:chart_date>', view_func=search.chart_exists)
app.add_url_rule('/search/<string:chart_date>', view_func=search.chart_search, methods=['GET', 'POST'])
app.add_url_rule('/search', view_func=search.search, methods=['GET', 'POST'])
app.add_url_rule('/random', view_func=search.random_chart, methods=['GET', 'POST'])

################### UTILITIES ###################
# 
#   See utilities.py for
#   
#   def root() returns the project's root / homepage 
#   def about() returns the about this project page
#   def loading_screen() supplies a loading modal for timed queries
#   def test_route() exists for temporary feature testing
#   def get_image(artist) is a route to test image scraping
#   
app.add_url_rule('/', view_func=utilities.root, methods=['GET', 'POST'])
app.add_url_rule('/about', view_func=utilities.about)
app.add_url_rule('/loading', view_func=utilities.loading_screen)
app.add_url_rule('/test', view_func=utilities.test_route)
app.add_url_rule('/images/<string:artist>', view_func=utilities.get_image, methods=['GET', 'POST'])

################### USER FAVORITES ###################

@app.route("/favorites/")
def show_favorites():

    form = NewSongForFavoriteList()

    songs = Song.query.all()

    # favorites = Favorite.query.get(user_id).all()
    
    form.song.choices(songs)

    return render_template('user_page.html', form=form, favorites=songs)

################### ERROR ###################

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

# @app.after_request
# def response_trigger(response):

#     """
#         Runs after giving a response to fetch additional image urls. 
#     """
#     @response.call_on_close
#     def process_after():
#         songs = Song.query.filter(Song.missing_page != True).limit(2)

#         for song in songs:
#             # Check if artist page has been searched for
#             if song.artist_page == "Not Queried":
            
#                 # Check if artist page search turned up empty
#                 if song.find_artist_page() != False:
                
#                     # Search for an image
#                     song.get_artist_image()
#                     print("fetched a song image")
        
#         pass
#     return response

################### AFTER (Caching) ###################
@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
