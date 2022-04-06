import os
from unittest import TestCase
from models import db, Chart, Song, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///flashback-test"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

app.config['WTF_CSRF_ENABLED'] = False

class TestUsers(TestCase):
    """ 
       Are favorites added and removed successfully across the site?
        
    """
    def setUp(self):
        """Add a new chart"""

        db.drop_all()
        db.create_all()
        

    def tearDown(self):
        """Clean up db"""

        db.session.rollback()

    def test_user_not_logged_in_redirect_to_signup(self):
        """ Trying to access /user without logging should send to signup"""

        with app.test_client() as client:
            resp = client.get('/user', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>FLASHBACK -  Signup </title>', html)
    
    def test_user_signed_up_redirect_to_profile(self):
        """ 
            New user sign up should redirect to profile.
        """

        with app.test_client() as client:
            d = {"username": "testabc", "password": "testabc"}
            client.post('/signup', data=d, follow_redirects=True)

            resp = client.get('/user', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('testabc', html)

    def test_user_signed_in_can_log_out_and_in(self):

        with app.test_client() as client:
            d = {"username": "testabc", "password": "testabc"}
            client.post('/signup', data=d, follow_redirects=True)

            resp = client.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Logged out', html)
            self.assertIn('Login', html)
            
            resp = client.get('/user', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please signup for an account or log in', html)

            resp = client.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testabc', html)

    def test_can_edit_user_profile(self):
        """
            Can a logged user access the update and update their birthday?
        
        """
        with app.test_client() as client:
            d = {"username": "testabc", "password": "testabc"}
            resp = client.post('/signup', data=d, follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn('testabc', html)
            self.assertIn('Add your birthday!', html)
            self.assertEqual(resp.status_code, 200)
            
            d = {"username": "testabc", "password": "testabc", "date_of_birth": "2000-01-01"}

            resp = client.post('/users/profile', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hot 100 Birthday Charts:', html)



    

          

            

            




################### ADDITIONAL INTEGRATION TESTS FROM user ROUTES IN app.py###################

#testing birthday charts / add birthday logic

#testing can update user profile
#testing can delete user profile