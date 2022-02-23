from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
import billboard
from forms import DateSearchForm, SignupForm
from models import db, connect_db, User

app = Flask(__name__)

app.config['SECRET_KEY'] = 'davessecret'

toolbar = DebugToolbarExtension(app)

# if __name__ == "__main__":
#     app.run(debug=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flashback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
db.create_all()


@app.route("/", methods=["GET", "POST"])
def root():
    """ Returns the root / index homepage"""
   
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    """A testing route for searches"""

    form = DateSearchForm()

    if form.validate_on_submit():
        date = form.date.data
        chart = billboard.ChartData('hot-100', date=date)
        return render_template("results.html", chart=chart)

    return render_template("search.html", form=form)

################### SIGNUP ###################

@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    """ Show a signup form"""

    if 'username' in session:
        return redirect(f"users/{session['username']}")
    
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data
        email = form.email.data
        profile_img_url = form.profile_img_url.data
        date_of_birth = form.date_of_birth.data

        new_user = User.signup(username, password, email, profile_img_url, date_of_birth)

        db.session.commit()
        session['username'] = new_user.username
        flash('Account created! Welcome, {new_user.username}.', 'success')
        return redirect(f"/users/{new_user.username}")

    return render_template("signup.html", form=form)


################### LOGIN ###################

# @app.route('/login')