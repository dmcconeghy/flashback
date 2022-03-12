from flask import render_template, flash, redirect, g, request
from models import Chart, Song, ChartAppearance, Favorite, db
from sqlalchemy import and_
from bs4 import BeautifulSoup
import requests

def show_list_of_charts(page=1):
    """ 
        Returns a paginated list of database stored charts showing their first five songs.
    
    """

    q = request.args.get('page')

    if q:
        charts = (Chart
                    .query
                    .order_by(Chart.chart_date.desc())
                    .paginate(page=q, per_page=1))
    else:
        charts = (Chart
                    .query
                    .order_by(Chart.chart_date.desc())
                    .paginate(page=page, per_page=1))

    chart_total = Chart.query.count()
    
    chart_list = []

    for chart in charts.items:
        
        ranked_appearances = (ChartAppearance
                                .query
                                .filter(ChartAppearance.chart_date == chart.chart_date.isoformat())
                                .order_by(ChartAppearance.rank)
                                .limit(5)
                                )

        ranked_song_ids = ([ra.song_id for ra in ranked_appearances])     

        song_objects = [Song.query.get(rsid) for rsid in ranked_song_ids]
    
        chart_merge = zip(song_objects, ranked_appearances)
        chart_list.append(chart_merge)

    favorites = [f.song_id for f in g.user.favorite_songs]
        
    return render_template('charts/charts.html', 
                                charts=charts, 
                                results=chart_list, 
                                favorites=favorites, 
                                chart_total=chart_total)

def show_list_of_charts_favorites(song_id):
    """Toggles a favorite song from the chart list to the user's favorites list"""

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
        return redirect(f"/charts")
    else:
        add_favorite = Favorite(
            user_id = g.user.id, 
            song_id=favorited_song.id)

        db.session.add(add_favorite)
        db.session.commit()

        added_favorite = Song.query.get_or_404(favorited_song.id)
        flash(f"Added {added_favorite.artist}'s {added_favorite.title} to your favorites", "success")

    return redirect(f"/charts")

def show_chart(req_chart_date):
    """ 
        Display a specific chart and its songs. Fetches image urls for every song.

        This route must occur AFTER validation through /exists.

        todo: fix issues with duplicate entries cf. "Unchained Melody" from 10.06.90 - 3.23.91
            There are two version on this chart but they're indistinguishable in single API data calls.
            The original peaked at #4 in 08.28.65 but *also* charted in 1990. 
            Presently, each duplicate entry adds a new Song entry, which isn't ideal. 
            There are likely many other such re-charts and duplication oddities to handle. 

        todo: Image URL retrieval currently overwrites urls rather than skipping them. 
            Ideally a logic check would prevent these, but the pairing of rank/song has to be precise. 
        
    """

    chart = Chart.query.filter(Chart.chart_date == req_chart_date).first()

    appearances = (
        ChartAppearance
        .query
        .filter(ChartAppearance.chart_date == req_chart_date)
        .order_by(ChartAppearance.rank)
        .all()
        )

    song_ids = [ra.song_id for ra in appearances]

    songs = [Song.query.get(sid) for sid in song_ids]

    favorites = [f.song_id for f in g.user.favorite_songs]

    return render_template('charts/chart_results.html', 
                                chart=chart, 
                                results=zip(songs, appearances), 
                                favorites=favorites)

def show_chart_favorites(chart_date, song_id):
    """Toggles a favorite song from the chart list to the user's favorites list"""

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
        return redirect(f"/chart/{chart_date}")
    else:
        add_favorite = Favorite(
            user_id = g.user.id, 
            song_id=favorited_song.id)

        db.session.add(add_favorite)
        db.session.commit()

        added_favorite = Song.query.get_or_404(favorited_song.id)
        flash(f"Added {added_favorite.artist}'s {added_favorite.title} to your favorites", "success")

    return redirect(f"/chart/{chart_date}")
