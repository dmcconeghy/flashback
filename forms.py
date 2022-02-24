from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, Length, URL, Optional 

class DateSearchForm(FlaskForm):
    """Homepage route search for chart from a specific date"""

    date = DateField("Enter a Date")
  
class SignupForm(FlaskForm):
    """ Signup form for a new user"""

    username = StringField("username", validators=[DataRequired(), Length(min = 1, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=100)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=75)])
    profile_img_url = StringField("Profile Image URL", validators=[URL(), Optional()])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])

class LoginForm(FlaskForm):
    """ Login form for an existsing user"""

    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])
    