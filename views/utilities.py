from flask import render_template
from idna import ulabel 
from models import ChartAppearance, Song, db, Chart
import requests
from bs4 import BeautifulSoup, SoupStrainer

################### PROJECT ROOT ###################    

def root():
    """ Returns the root / index homepage"""

    return render_template('index.html')

################### PROJECT ABOUT ###################    

def about():
    """ Returns the about page"""

    return render_template('navbar/about.html')

################### PROJECT FEATURES ###################    

def features():
    """ Returns the features page"""

    return render_template('navbar/features.html')


################### LOADING ###################

def loading_screen():

    return render_template('loading.html')

################### TEST ###################

def test_route():

    test = db.session.query(Song.id, Song.title).limit(10).all()

    print(test)
    return render_template('test.html')

################### ARTIST IMAGE ###################

def get_artist_image(artist):

    hyphen_artist = artist.replace('&20', '-')
    space_artist = artist.replace('-', ' ').title()

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

    return render_template('songs/fetch_song_art.html',
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

################### CHART IMAGEs ###################

def get_chart_images(chart_date):

    
    BASE_URL = "http://billboard.com/charts/hot-100/"

    URL = BASE_URL + chart_date
    

    def get_data(url):
        r = requests.get(url)
        if r.status_code != 404:
            return r.text
        else:
            return "Not Found"
    
    htmldata = get_data(URL)

    if htmldata != "Not Found":
        raw = BeautifulSoup(htmldata, 'html.parser')

        chart_results = raw.select_one('.chart-results-list')

        results_list = chart_results.select('.o-chart-results-list-row')

        img_elements = []

        for result in results_list:

            img_elements += result.select("img")

        # srcs = img_elements.find_all('data-lazy-src')

        srcs = []

        for element in img_elements:
            srcs.append(element['data-lazy-src'])

        chart_object = Chart.query.filter(Chart.chart_date==chart_date).first()

        ranked_appearances = (ChartAppearance
            .query
            .filter(ChartAppearance.chart_date == chart_date)
            .order_by(ChartAppearance.rank)
            .all())
  
        ranked_song_ids = ([
            ra.song_id for ra in ranked_appearances
        ])

        src_and_song_id_merge = zip(srcs, ranked_song_ids)
        
        for src, id in src_and_song_id_merge:

            entry = Song.query.get(id)
            entry.song_img_url = src
            db.session.commit()

        ranked_song_objects = ([
            Song.query.get(ra.song_id) for ra in ranked_appearances])

    return render_template('songs/fetch_chart_art.html',
                            chart_date=chart_date,
                            URL=URL,
                            soup=srcs,
                            chart_object=chart_object.chart_date,
                            songs=ranked_song_objects, 
                            img_elements=img_elements                            
                            )
