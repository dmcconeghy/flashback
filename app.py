import os

from flask import Flask, render_template, redirect, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import and_

from models import db, connect_db, User, Song, Favorite
from forms import SignupForm, LoginForm, NewSongForFavoriteList, UpdateProfile, DeleteProfileForm
import views.chart as chart
import views.song as song
import views.search as search
import views.utilities as utilities
import datetime

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
    """ 
    
        Show a signup form to users not logged in session. 

        Has minor logic for birthdate validation. 
        Additional form validation by WTForms 
    
    
    """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    # if 'username' in session:
    #     return redirect(f"users/{session['username']}")
    
    form = SignupForm()

    if form.validate_on_submit():

        if form.date_of_birth.data and form.date_of_birth.data >= datetime.date.today():
            flash("You haven't been born yet!", 'danger')
            return render_template("users/signup.html", form=form)

        if form.date_of_birth.data and form.date_of_birth.data <= datetime.date(1903, 1, 2):
            flash("You're older than Kane Tanaka, the oldest person alive!", 'danger')
            return render_template("users/signup.html", form=form)


        # WTForms has deprecated the unique validator. We need to check for duplicate usernames or risk a db error.
        # With a small number of usernames, this is a quick fix. At scale we should write a custom validator. 
         
        if (User.query.filter(User.username == form.username.data).first()) is not [] or None: 
            flash("Your chosen username is already take. Please select another.", 'warning')
            return render_template("users/signup.html", form=form)

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

        return render_template("users/signup.html", form=form)

################### USER LOGIN ###################

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ 
    
        Handle user login 
    
    """

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(f"/users/{user.id}")
        
        flash("Invalid username or password", "danger")

    return render_template('users/login.html', form=form)

################### USER PROFILE PAGE ###################
@app.route('/user')
def user_redirect():

    """
        Prevents non-logged users from accessing user pages. 
    
    """


    if not g.user:
        flash("Please signup for an account or log in", "warning")
        return redirect("/signup")

    return redirect(f"/users/{g.user.id}")

@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def show_user_page(user_id):
    """
    
        Show a logged in user their personal user page. 

        This loads user profile details including favorite songs, and birthday charts. 

        Allows quick removal of user favorites or 
        option to add a favorite from a preselected list of non-favorited songs. 
    
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    if user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    form = NewSongForFavoriteList()

    favorites = Favorite.query.filter(Favorite.user_id == user_id).all()
    favorites_ids = [f.song_id for f in favorites]

    songbank = Song.query.filter(Song.id.notin_(favorites_ids)).limit(20).all()
    # songbank_ids = [s.id for s in songbank]

    form.song.choices = [(s.id, (f"{s.title} by {s.artist}")) for s in songbank]
        
    songs = [Song.query.get(sid) for sid in favorites_ids]

    if form.validate_on_submit():

        add_favorite = Favorite(
                            user_id=user.id, 
                            song_id=form.song.data)

        db.session.add(add_favorite)
        db.session.commit()

        # Renewing these variable's contents
        # This ensures the reload contains updated information. 
        favorites = Favorite.query.all()
        favorites_ids = [f.song_id for f in favorites]

        songbank = Song.query.filter(Song.id.notin_(favorites_ids)).limit(10).all()
        # songbank_ids = [s.id for s in songbank]

        form.song.choices = [(s.id, s.title) for s in songbank]

        songs = [Song.query.get(sid) for sid in favorites_ids]

        added_song = Song.query.get(form.song.data)

        flash(f"Added {added_song.title} to your favorites!", 'success')

        return render_template("users/user_page.html", 
                            user=user, 
                            form=form, 
                            favorites=favorites,
                            favorites_ids=favorites_ids, 
                            songs=songs)
        
    return render_template("users/user_page.html", 
                            user=user, 
                            form=form, 
                            favorites=favorites,
                            favorites_ids=favorites_ids, 
                            songs=songs)

################### USER LOGOUT ###################

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash(f"Logged out", "success")
    
    return redirect("/login")

################### USER PROFILE REMOVE FAVORITE ###################

@app.route('/users/<int:user_id>/removefavorite/<int:song_id>', methods=['POST'])
def remove_favorites(user_id, song_id):

    """
    
        Removes favorites from the user's profile page. 
    
    """

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    if user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    
    favorite_ids = [f.song_id for f in user.favorite_songs]

    if song_id in favorite_ids:

        remove_favorite = (Favorite
                            .query
                            .filter(
                            and_(
                                Favorite.user_id==user_id, 
                                Favorite.song_id==song_id)
                                )
                            .first())


        db.session.delete(remove_favorite)
        db.session.commit()    

    removed_favorite = Song.query.get_or_404(song_id)

    flash(f"{removed_favorite.artist}'s {removed_favorite.title} removed from your favorites", "warning")

    return redirect(f"/users/{user_id}")

################### UPDATE USER PROFILE ###################

@app.route('/users/profile', methods=['GET', 'POST'])
def update_profile():

    """
    
        Allows a logged and authenticated user access to update their profile. 
        Includes validation for user birthday charts date entry. 
        Requires valid credentials to save changes. 
    
    """

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')
    
    user=g.user

    form=UpdateProfile(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):

            if form.date_of_birth.data and form.date_of_birth.data >= datetime.date.today():
                flash("You haven't been born yet!", 'danger')
                return render_template("/users/edit.html", form=form, user=user)

            if form.date_of_birth.data and form.date_of_birth.data <= datetime.date(1903, 1, 2):
                flash("You're older than Kane Tanaka, the oldest person alive!", 'danger')
                return render_template("/users/edit.html", form=form, user=user)

            user.username = form.username.data
            user.email = form.email.data
            if validators.url(form.profile_img_url.data) or form.profile_img_url.data == "/static/media/blank_profile.png":
                user.profile_img_url = form.profile_img_url.data
            else:
                form.profile_img_url.data == "/static/media/blank_profile.png"

            user.date_of_birth = form.date_of_birth.data

            db.session.commit()
            return redirect(f"/users/{user.id}")
        
        flash("Invalid credentials.", 'danger')
           
    return render_template('/users/edit.html', form=form, user=user)

################### UPDATE USER PROFILE ###################

@app.route('/users/delete', methods=['GET','POST'])
def delete_profile():
    """
        If authorized and logged in, allows a user to delete their profile. 
    
    """

    if not g.user:
            flash("Access Unauthorized. Please Log in", "danger")
            return redirect('/') 

    user=g.user

    form = DeleteProfileForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):

            do_logout()

            db.session.delete(user)
            db.session.commit()
            flash("Profile Deleted.", "success")
            return redirect('/')

        flash("Invalid credentials.", 'danger')

    return render_template('/users/delete.html', form=form)

################### CHARTS ################### 
#
#   See charts.py for:
# 
#   def show_list_of_charts / show_list_of_charts(page) for all charts in the database
#   def show_chart(req_chart_date) for a specific date's chart
#   def show_list_of_charts_favorites & show_chart_favorites add user favorite feature
#     
#
app.add_url_rule('/charts', view_func=chart.show_list_of_charts, methods=['GET', 'POST'])
app.add_url_rule('/charts/<int:page>', view_func=chart.show_list_of_charts, methods=['GET', 'POST'])
app.add_url_rule('/chart/<string:req_chart_date>', view_func=chart.show_chart, methods=['GET', 'POST'])
app.add_url_rule('/chart/<string:chart_date>/favorite/<int:song_id>', view_func=chart.show_chart_favorites, methods=['POST'])
app.add_url_rule('/charts/<int:page>/favorite/<int:song_id>', view_func=chart.show_list_of_charts_favorites, methods=['POST'])
################### SONG/S ################### 
#
#   See song.py for
#  
#   def show_list_of_songs(page=1) for a paginated list of songs in the database
#   def show_song_details(song_id) for a detailed song page
#   def show_song_gallery() for a gallery version of a selection of songs in the database
#   def listing() for a jukebox style version of chart information | Not fully implemented in v1.
#   def toggle_songs_like & toggle_song_like add user favorite feature.
# 
app.add_url_rule('/songs', view_func=song.show_list_of_songs, methods=['GET', 'POST'])
app.add_url_rule('/songs/<int:page>', view_func=song.show_list_of_songs, methods=['GET', 'POST'])
app.add_url_rule('/song/<int:song_id>', view_func=song.show_song_details)
app.add_url_rule('/songs/gallery', view_func=song.show_song_gallery)
app.add_url_rule('/listing', view_func=song.listing)
app.add_url_rule('/songs/<int:page>/favorite/<int:song_id>', view_func=song.toggle_songs_like, methods=["POST"])
app.add_url_rule('/song/<int:song_id>/favorite', view_func=song.toggle_song_like, methods=['POST'])

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
#   def get_artist_image(artist) is a route to test image scraping for individual artists | deprecated / test-only
#   def get_chart_images(chart_date) is a route to test image scraping for chart instances | deprecated / test-only
#   
app.add_url_rule('/', view_func=utilities.root, methods=['GET', 'POST'])
app.add_url_rule('/about', view_func=utilities.about)
app.add_url_rule('/loading', view_func=utilities.loading_screen)
app.add_url_rule('/test', view_func=utilities.test_route)
app.add_url_rule('/images/<string:artist>', view_func=utilities.get_artist_image, methods=['GET', 'POST'])
app.add_url_rule('/features', view_func=utilities.features)
app.add_url_rule('/chart/images/<string:chart_date>', view_func=utilities.get_chart_images, methods=['GET', 'POST'])


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
