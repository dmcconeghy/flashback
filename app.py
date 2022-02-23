from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
import billboard

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


@app.route("/")
def root():
    return render_template("index.html")

@app.route("/test")
def test():

    chart = billboard.ChartData('hot-100')


    return render_template("test.html", chart=chart)
