from flask import render_template 
from models import Song, db
import requests
from bs4 import BeautifulSoup

################### PROJECT ROOT ###################    

def root():
    """ Returns the root / index homepage"""

    return render_template('index.html')

################### PROJECT ABOUT ###################    

def about():
    """ Returns the about page"""

    return render_template('about.html')

################### LOADING ###################

def loading_screen():

    return render_template('loading.html')

################### TEST ###################

def test_route():

    return render_template('test.html')

################### ARTIST IMAGE ###################

def get_image(artist):

    hyphen_artist = artist.replace('&20', '-')
    space_artist = artist.replace('&20', ' ').title()

    formatted_url = f"http://billboard.com/artist/{hyphen_artist}"

    def get_data(url):
        r = requests.get(url)
        if r.status_code != 404:
            return r.text
        else:
            return "Not Found"
    
    htmldata = get_data(formatted_url)

    if htmldata != "Not Found":
        soup = BeautifulSoup(htmldata, 'html.parser')
        alt=f"An image of {space_artist}"
    
        img_element = soup.find('img', alt=alt)
    else:
        soup = "Not Found"
        alt=f"An image of {space_artist}"
        img_element = None
    
    if img_element != None:
       
        image_src = img_element['data-lazy-src']

        songs = Song.query.filter(Song.artist == space_artist).all()

        for song in songs:
            song.song_img_url = image_src
            db.session.commit()
    else:
        image_src = "def"
        songs = Song.query.filter(Song.artist == space_artist).all()

    return render_template('images.html',
                            artist=artist, 
                            hyphen_artist=hyphen_artist,
                            space_artist=space_artist,
                            formatted_url=formatted_url,
                            img_element=img_element,
                            alt=alt, 
                            image_src=image_src,  
                            songs=songs, 
                            soup=soup, 
                            )
