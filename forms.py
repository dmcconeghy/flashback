from flask_wtf import FlaskForm
from wtforms import DateField

class DateSearchForm(FlaskForm):
    """Homepage route search for chart from a specific date"""

    date = DateField("Enter a Date")
  
