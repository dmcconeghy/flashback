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

class TestSearchRoute(TestCase):
    """ Tests the search page & search form loading """

    def test_signup_page(self):
        with app.test_client() as client:
            """ Did the signup page load?"""
            resp = client.get('/search')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h3 class="pb-5">Explore Billboard\'s Hot 100!</h3>',  html)
            

    def test_signup_form(self):
        """ Is the search form appearing?"""
        with app.test_client() as client:
            resp = client.get('/search')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<label for="date">Enter a Date after August 4, 1958</label>',  html)
            self.assertIn('<button id="randomize" class="btn btn-small btn-secondary justify-content-top mx-1" formaction="/random" data-toggle="modal" data-target="#loadingModal">Random</button>',  html)

class TestSearchForm(TestCase):
    """ 
        Does the Random Chart feature work?
        Does it handle bad data inputs?
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

    def test_search_handles_bad_random_date(self):
        """ 
            Is the search form handling bad inputs?

            Testing a successful API redirect results in the following error:
            ResourceWarning: unclosed <ssl.SSLSocket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('172.17.251.128', 55022), raddr=('192.0.66.192', 443)>
                self.fetchEntries()
        
        """
        with app.test_client() as client:
            d = {"date" : "1900-01-01"}
        
            resp = client.post('/search', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-warning">Oldest Chart is from August 4th, 1958!</div>',  html)

        with app.test_client() as client:
            d = {"date" : "2100-01-01"}
        
            resp = client.post('/search', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            
            self.assertIn('<div class="alert alert-warning">Can&#39;t Tell the Future!</div>',  html)

        with app.test_client() as client:
            db.drop_all()
            db.create_all()
            d = {"date": "1999-01-01"}

            resp = client.post('/search',data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>The Hot 100 on January 02, 1999 </h1>', html)


class TestChartExists(TestCase):

    def test_chart_exists_returns_existing_chart(self):
        """
            With a known chart, does that page's chart exist?
            This chart also tests chart_search's input of Chart data to db
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

        with app.test_client() as client:
            
            d = {"date" : "1999-01-02"}
        
            resp = client.post('/search', data=d, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            resp = client.get('/chart/1999-01-02', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>The Hot 100 on January 02, 1999 </h1>', html)

class TestChartFetchRoute(TestCase):

    def setUp(self):
        """Add a new chart"""

        Chart.query.delete()

        with app.test_client() as client:
            d = {"date" : "1999-01-02"}
            client.post('/search', data=d, follow_redirects=True)

    def tearDown(self):
        """Clean up db"""

        db.session.rollback()

    def test_songs_added(self):
        """ Do songs from chart now exist? """

        with app.test_client() as client:
            resp = client.get('/chart/1999-01-02')
            html = resp.get_data(as_text=True)
            self.assertIn('I&#39;m Your Angel by R. Kelly &amp; Celine Dion', html)
    
    def test_appearance_data_added(self):
        """ Do songs' chart appearance data exist"""

        with app.test_client() as client:
            resp = client.get('/chart/1999-01-02')
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="col-sm-1 text-center"> 1\n            </div>', html)
    
    def test_song_image_appears(self):
        """ Did the image fetching route fetch an image?"""

        with app.test_client() as client:
            resp = client.get('/chart/1999-01-02')
            html = resp.get_data(as_text=True)
            self.assertIn('<img class="img-fluid img-thumbnail" src="https://charts-static.billboard.com/img/1990/10/celine-dion-0hi-180x180.jpg" alt="default album image" width="50px">', html)
    
    def test_missing_song_image(self):
        """ Did a song with no chart image display the default missing image?"""

        with app.test_client() as client:
            resp = client.get('/chart/1999-01-02')
            html = resp.get_data(as_text=True)
            self.assertIn('<img class="img-fluid img-thumbnail" src="../static/media/missing_album_art.svg" alt="default album image" width="50px">', html)
    


################### ADDITIONAL INTEGRATION TESTS FROM ROUTES IN search.py###################

#testing chart_search that new chart doesn't add pre-existing song 
#testing chart_search that new chart adds new chart appearance for pre-existing song
#testing chart_search that new chart image get_data route for 404 or requests data