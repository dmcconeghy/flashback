from flask import render_template, request, g, flash, redirect
from models import Chart, Song, ChartAppearance, Favorite, db
import requests
from sqlalchemy import and_



def show_list_of_songs(page=1):
    """ Returns a list of database stored songs from queried charts """
    q = request.args.get('page')

    if q:
        songs = Song.query.order_by(Song.id).paginate(page=q, per_page=10)
    else:
        songs = Song.query.order_by(Song.id).paginate(page=page, per_page=10)
    
    chart_total = Chart.query.count()

    # response = Song.query.order_by(Song.id).all()

    # for song in all_songs:
    #     # Check if artist page has been searched for
    #     if song.artist_page == "Not Queried":
            
    #         # Check if artist page search turned up empty
    #         if song.find_artist_page() != False:
                
    #             # Search for an image
    #             song.get_artist_image()

    if not g.user:
        
        favorites=[]

    else:

        favorites = [f.song_id for f in g.user.favorite_songs]
         
    return render_template('songs/songs.html', songs=songs, chart_total=chart_total, favorites=favorites)

def show_song_details(song_id):

    song = Song.query.get_or_404(song_id)
    
    # Check if artist page has been searched for
    if song.artist_page == "Not Queried":
        
        # Check if artist page search turned up empty
        if song.find_artist_page() != False:
            
            # Search for an image
            song.get_artist_image()
                
    favorites = [f.song_id for f in g.user.favorite_songs]
        
    appearances = ChartAppearance.query.filter(ChartAppearance.song_id == song_id).all()
    
    return render_template('songs/song.html', song=song, appearances=appearances, favorites=favorites)


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

    return render_template('songs/song_gallery.html', songs=songs)

def listing():

    songs = Song.query.limit(20).all()

    return render_template('songs/listing.html', songs=songs)


def toggle_songs_like(page, song_id):
    """Toggles a favorite song from the songs list to the user's favorites list"""

    if not g.user:
        flash("You need to log in to save favorites.", "warning")
        return redirect("/")

    favorited_song = Song.query.get_or_404(song_id)
    
    favorite_ids = [f.song_id for f in g.user.favorite_songs]

    if favorited_song.id in favorite_ids:

        remove_favorite = (Favorite
                            .query
                            .filter(
                            and_(
                                Favorite.user_id==g.user.id, 
                                Favorite.song_id==favorited_song.id)
                                )
                            .first())

        db.session.delete(remove_favorite)
        db.session.commit()

        removed_favorite = Song.query.get_or_404(favorited_song.id)

        flash(f"{removed_favorite.artist}'s {removed_favorite.title} removed from your favorites", "warning")
        return redirect(f"/songs/{page}")
    else:
        add_favorite = Favorite(
            user_id = g.user.id, 
            song_id=favorited_song.id)

        db.session.add(add_favorite)
        db.session.commit()

        added_favorite = Song.query.get_or_404(favorited_song.id)
        flash(f"Added {added_favorite.artist}'s {added_favorite.title} to your favorites", "success")

    return redirect(f"/songs/{page}")

def toggle_song_like(song_id):
    """Toggles a favorite song from the song page for the user's favorites list"""

    if not g.user:
        flash("You need to log in to save favorites.", "warning")
        return redirect("/")

    favorited_song = Song.query.get_or_404(song_id)

    favorite_ids = [f.song_id for f in g.user.favorite_songs]

    if favorited_song.id in favorite_ids:

        remove_favorite = (Favorite
                            .query
                            .filter(
                            and_(
                                Favorite.user_id==g.user.id, 
                                Favorite.song_id==favorited_song.id)
                                )
                            .first())

        db.session.delete(remove_favorite)
        db.session.commit()

        removed_favorite = Song.query.get_or_404(favorited_song.id)

        flash(f"{removed_favorite.artist}'s {removed_favorite.title} removed from your favorites", "warning")
        return redirect(f"/song/{song_id}")
    else:
        add_favorite = Favorite(
            user_id = g.user.id, 
            song_id=favorited_song.id)

        db.session.add(add_favorite)
        db.session.commit()

        added_favorite = Song.query.get_or_404(favorited_song.id)
        flash(f"Added {added_favorite.artist}'s {added_favorite.title} to your favorites", "success")

    return redirect(f"/song/{song_id}")