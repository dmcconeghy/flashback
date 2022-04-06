import os
from unittest import TestCase

from models import db, Chart, Song

os.environ['DATABASE_URL'] = "postgresql:///flashback-test"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class TestCharts(TestCase):
    """ 
        Does the Chart page show retrieved charts?
        
    """
    def setUp(self):
        """Add a new chart"""

        Chart.query.delete()
        Song.query.delete()

        with app.test_client() as client:
            d = {"date" : "1999-01-02"}
            client.post('/search', data=d, follow_redirects=True)

    def tearDown(self):
        """Clean up db"""

        db.session.rollback()

    def test_show_all_charts(self):
        """ 
            With a known chart in the db, does the show all charts page display it? 
        
        """
        with app.test_client() as client:
            d = {"date" : "1900-01-01"}
        
            client.post('/search', data=d, follow_redirects=True)
            
            resp = client.get('/charts', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a href="/chart/1999-01-02">Week of January 02, 1999</a>',  html)

################### ADDITIONAL INTEGRATION TESTS FROM ROUTES IN chart.py###################

# Favorite routes are testing in test_favorites.py