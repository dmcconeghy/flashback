from flask_wtf import FlaskForm
from wtforms import DateField, StringField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, URL, Optional 

class DateSearchForm(FlaskForm):
    """
    
    Homepage route search for chart from a specific date.
    Date validation logic found in search.py
    
    """

    date = DateField("Enter a Date after August 4, 1958")
  
class SignupForm(FlaskForm):
    """ Signup form for a new user"""

    username = StringField("Username (required)", validators=[DataRequired(), Length(min = 1, max=20)])
    password = PasswordField("Password (required)", validators=[DataRequired(), Length(min=6, max=100)])
    email = EmailField("Email", validators=[Optional(), Email(), Length(max=75)])
    profile_img_url = StringField("Profile Image URL", validators=[URL(), Optional()])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])

class LoginForm(FlaskForm):
    """ Login form for an existsing user"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])

class NewSongForFavoriteList(FlaskForm):
    """ Form for adding songs to favorites """

    song = SelectField('Add Randomly selected songs to your favorites!', coerce=int)

class UpdateProfile(FlaskForm):
    """Form for updating a user's' profile"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[Optional(), Email()])
    profile_img_url = StringField('Image URL', validators=[URL(), Optional()])
    date_of_birth = DateField("Date of Birth", validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class BirthdayUpdateForm(FlaskForm):
    """Form for updating just a user's birthday when it is missing from their profile"""

    date_of_birth = DateField("Date of Birth", validators=[Optional()])

class DeleteProfileForm(FlaskForm):
    """ Delete your profile"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])