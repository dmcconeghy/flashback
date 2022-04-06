import os
from unittest import TestCase

from models import db

os.environ['DATABASE_URL'] = "postgresql:///flashback-test"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class SignUpTestCase(TestCase):
    """ Test signup get route"""

    def test_signup_page(self):
        with app.test_client() as client:
            """ Did the signup page load?"""
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Sign Up</h1>',  html)

    def test_signup_form(self):
        """ Is the signup form appearing?"""
        with app.test_client() as client:
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Register</button>',  html)

class LoginTestCase(TestCase):
    """ Test login get route"""

    def test_login_page(self):
        """ Did the login page load?"""
        with app.test_client() as client:           
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Login</h1>',  html)
    
    def test_login_form(self):
        """ Is the login form appearing?"""
        with app.test_client() as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Login</button>',  html)

class Is404TestCase(TestCase):
    """Does the 404 page show?"""

    def test_404_page(self):
        with app.test_client() as client:
            resp = client.get('/doesntexist')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn("I Still Haven't Found What I'm Looking For", html)


################### ADDITIONAL INTEGRATION TESTS FROM ROUTES IN app.py###################

#testing do_login and do_logout
#testing logged in user arrival at /signup or /login
#testing login in as user
#testing logout as user
#testing signup as new user
#testing unauthorized acces to user profile
#testing user profile page
#testing favorites form user page
#testing birthday charts / add birthday logic
#testing adding and removing favorites from user page
#testing can update user profile
#testing can delete user profile
