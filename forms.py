from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, Length, URL, Optional

class DateSearchForm(FlaskForm):
    """Homepage route search for chart from a specific date"""

    date = DateField("Enter a Date")
  
class SignupForm(FlaskForm):
    """ Signup form for a new user"""

    username = StringField("username", validators=[InputRequired(), Length(min = 1, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=100)])
    email = EmailField("Email", validators=[InputRequired(), Email(), Length(max=75)])
    profile_img_url = StringField("Profile Image URL", validators=[URL(), Optional()])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
