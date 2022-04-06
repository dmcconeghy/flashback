import os
from unittest import TestCase
from flask import session
from models import db, Chart, Song, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///flashback-test"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class TestFavorites(TestCase):
    """ 
       Are favorites added and removed successfully across the site?
        
    """
    def setUp(self):
        """Add a new chart"""

        Chart.query.delete()
        Song.query.delete()

        with app.test_client() as client:
            d = {"date" : "1999-01-02"}
            client.post('/search', data=d, follow_redirects=True)
        
        User.query.delete()

        with app.test_client() as client:
            d = {"username": "testabc", "password": "testabc"}
            client.post('/signup', data=d, follow_redirects=True)

        Favorite.query.delete()

    def tearDown(self):
        """Clean up db"""

        db.session.rollback()

    def test_add_remove_songs_page(self):
        """
            First check that no songs have been favorited.
            Then add a favorite and check that it has been added.
            Then remove the favorite and check it has been removed.
        """
        with app.test_client() as client:
            client.post("/login", data={"username": "testabc", "password": "testabc"})

            d = {"user_id": 1, "song_id": 1}

            resp = client.get('/songs/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/songs/1/favorite/1', data=d, follow_redirects=True)

            resp = client.get('/songs/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/songs/1/favorite/1', data=d, follow_redirects=True)

            resp = client.get('/songs/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

    def test_add_remove_song_page(self):
        """
            First check that the song is not favorited.
            Then add a favorite and check that it has been added.
            Then remove the favorite and check it has been removed.
        """
        with app.test_client() as client:
            client.post("/login", data={"username": "testabc", "password": "testabc"})

            d = {"user_id": 1, "song_id": 1}

            resp = client.get('/song/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/song/1/favorite', data=d, follow_redirects=True)

            resp = client.get('/song/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/song/1/favorite', data=d, follow_redirects=True)

            resp = client.get('/song/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

    def test_add_remove_songs_page(self):
        """
            First check that no songs have been favorited.
            Then add a favorite and check that it has been added.
            Then remove the favorite and check it has been removed.
        """
        with app.test_client() as client:
            client.post("/login", data={"username": "testabc", "password": "testabc"})

            d = {"user_id": 1, "song_id": 1}

            resp = client.get('/songs/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/songs/1/favorite/1', data=d, follow_redirects=True)

            resp = client.get('/songs/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/songs/1/favorite/1', data=d, follow_redirects=True)

            resp = client.get('/songs/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

    def test_add_remove_charts_page(self):
        """
            First check that the song is not favorited.
            Then add a favorite and check that it has been added.
            Then remove the favorite and check it has been removed.
        """
        with app.test_client() as client:
            client.post("/login", data={"username": "testabc", "password": "testabc"})

            d = {"user_id": 1, "song_id": 1}

            resp = client.get('/charts/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/charts/1/favorite/1', data=d, follow_redirects=True)

            resp = client.get('/charts/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/charts/1/favorite/1', data=d, follow_redirects=True)

            resp = client.get('/charts/1')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

    def test_add_remove_chart_page(self):
        """
            First check that the song is not favorited.
            Then add a favorite and check that it has been added.
            Then remove the favorite and check it has been removed.
        """
        with app.test_client() as client:
            client.post("/login", data={"username": "testabc", "password": "testabc"})

            d = {"user_id": 1, "song_id": 1}

            resp = client.get('chart/1999-01-02')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/chart/1999-01-02/favorite/1', data=d, follow_redirects=True)

            resp = client.get('chart/1999-01-02')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<i class="fa-solid fa-star"></i>',  html)

            client.post('/chart/1999-01-02/favorite/1', data=d, follow_redirects=True)

            resp = client.get('chart/1999-01-02')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<i class="fa-solid fa-star"></i>',  html)
