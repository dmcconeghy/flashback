from flask import render_template, request
from models import Chart, Song, ChartAppearance

def show_list_of_artists(page=1):
    """ Returns a list of database stored artists from queried charts """
    q = request.args.get('page')

    if q:
        artists = Song.query.order_by(Song.artist).paginate(page=q, per_page=10)
    else:
        artists = Song.query.order_by(Song.artist).paginate(page=page, per_page=10)
    
    chart_total = Chart.query.count()
        
    return render_template('artists.html', artists=artists, chart_total=chart_total)

def show_artist_details(artist_name):

    songs = Song.query.filter(Song.artist == artist_name).all()

    name=artist_name

    song_ids = [s.id for s in songs]
   
    appearances = [ChartAppearance.query.filter(ChartAppearance.song_id == sids).all() for sids in song_ids] 
     
    return render_template('artist.html', artist_name=name, songs=songs, appearances=appearances)
