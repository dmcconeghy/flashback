from flask import render_template, request
from models import Chart, Song, ChartAppearance
import requests


def show_list_of_songs(page=1):
    """ Returns a list of database stored songs from queried charts """
    q = request.args.get('page')

    if q:
        songs = Song.query.order_by(Song.id).paginate(page=q, per_page=10)
    else:
        songs = Song.query.order_by(Song.id).paginate(page=page, per_page=10)
    
    chart_total = Chart.query.count()

    response = Song.query.order_by(Song.id).all()

    # for song in all_songs:
    #     # Check if artist page has been searched for
    #     if song.artist_page == "Not Queried":
            
    #         # Check if artist page search turned up empty
    #         if song.find_artist_page() != False:
                
    #             # Search for an image
    #             song.get_artist_image()
        
    return render_template('songs.html', songs=songs, chart_total=chart_total)

def show_song_details(song_id):

    song = Song.query.get_or_404(song_id)
    
    # Check if artist page has been searched for
    if song.artist_page == "Not Queried":
        
        # Check if artist page search turned up empty
        if song.find_artist_page() != False:
            
            # Search for an image
            song.get_artist_image()
                

        
    appearances = ChartAppearance.query.filter(ChartAppearance.song_id == song_id).all()
    
    return render_template('song.html', song=song, appearances=appearances)


def show_song_gallery():
    """ Returns a scrollable gallery of songs. """

    songs = Song.query.limit(20).all()

    for song in songs:
        # Check if artist page has been searched for
        if song.artist_page == "Not Queried":
            
            # Check if artist page search turned up empty
            if song.find_artist_page() != False:
                
                # Search for an image
                song.get_artist_image()

    return render_template('song_gallery.html', songs=songs)

def fetch_song_art(song_id):
    """ 
        Fetches a specific song's album art using the iTunes API.
        This FAILS because requests executes BEFORE Song.query returns a result.  
    
    """
    song = Song.query.get_or_404(song_id)

    artist = song.artist
    title = song.title

    a = artist.replace(' ', '+')

    t = title.replace(' ', '+')


    r = requests.get('https://itunes.apple.com/search?term={{a}}&entity=musicArtist&limit=5').json()

    return render_template('fetch_art.html', song=song, a=a, r=r)

def listing():

    songs = Song.query.limit(20).all()

    return render_template('listing.html', songs=songs)