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

class TestSongRoutes(TestCase):

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

    def test_show_all_songs(self):
        """ Checking songs for known songs"""

        with app.test_client() as client:
            resp = client.get('/songs')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Returned 100 songs from 1 charts.', html)

    def test_show_one_songs(self):
        """ Checking songs/song.song.html for known songs"""

        with app.test_client() as client:
            resp = client.get('/song/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('I&#39;m Your Angel', html)
        
################### ADDITIONAL INTEGRATION TESTS FROM ROUTES IN search.py###################

#testing song_gallery -- feature deprecated
#testing listing -- feature deprecated
#testing song likes -- see test_favorites
