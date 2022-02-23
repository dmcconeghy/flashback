from flask import Flask, render_template, redirect
from flask_debugtoolbar import DebugToolbarExtension
import billboard
from forms import DateSearchForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'davessecret'

toolbar = DebugToolbarExtension(app)

if __name__ == "__main__":
    app.run(debug=True)


# app.config['SQLALCHEMY_DATABASE_URI'] = 
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# connect_db(app)
# db.create_all()


@app.route("/", methods=["GET", "POST"])
def root():

   
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():

    form = DateSearchForm()

    if form.validate_on_submit():
        date = form.date.data
        chart = billboard.ChartData('hot-100', date=date)
        return render_template("results.html", chart=chart)

    return render_template("search.html", form=form)
