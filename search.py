from flask import render_template, redirect, flash
from models import Chart, Song, ChartAppearance, db
import billboard
import random
import datetime
from forms import DateSearchForm
from sqlalchemy import and_


def chart_exists(chart_date):

    def previously_fetched(date_to_be_checked):
        """ 
            Does our chart date exist already? 
            Yes? Return db version.
            No? Fetch it. 
        """
        
        found_chart = (Chart
                    .query
                    .filter(Chart.chart_date == date_to_be_checked)
                    .all()) 

        if found_chart:
            return True
        else:
            return False

    if previously_fetched(chart_date):
        flash('Chart found', 'success')
        return redirect(f"/chart/{chart_date}")
        
    else:

        return redirect(f"/search/{chart_date}")
        
def chart_search(chart_date):
    """ 
    Creates a chart entry and populates the db with songs and appearance data.
    """

    fetched_chart = billboard.ChartData('hot-100', date=chart_date)

    new_chart = Chart(
        name=fetched_chart.name,
        chart_date=fetched_chart.date
        # consider fetching chartData for entries?
    )

    db.session.add(new_chart)
    db.session.commit()

    for entry in fetched_chart:

        # Check if it is in our db already
        song_exists = Song.query.filter(and_(Song.title == entry.title, Song.artist == entry.artist)).first()
        
        if song_exists != [] and song_exists != None:
            
            # Check that the appearance data is different (e.g, 1990-11-11 Unchained Meloday appears twice)
            if ChartAppearance.query.filter(and_(ChartAppearance.song_id == song_exists.id, ChartAppearance.chart_date == fetched_chart.date)).first():
                new_song = Song(
                    title = entry.title, 
                    artist = entry.artist,
                )

                db.session.add(new_song)
                db.session.commit()

                new_appearance = ChartAppearance(
                    chart_id = new_chart.id,
                    song_id = new_song.id,
                    peak_pos = entry.peakPos,
                    last_pos = entry.lastPos,
                    weeks = entry.weeks,
                    rank = entry.rank,
                    isNew = entry.isNew,
                    chart_date = new_chart.chart_date
                )

            else: 
                new_appearance = ChartAppearance(
                    chart_id = new_chart.id,
                    song_id = song_exists.id,
                    peak_pos = entry.peakPos,
                    last_pos = entry.lastPos,
                    weeks = entry.weeks,
                    rank = entry.rank,
                    isNew = entry.isNew,
                    chart_date = new_chart.chart_date
                )

                db.session.add(new_appearance)
                db.session.commit()

        else:
            

            new_song = Song(
                title = entry.title, 
                artist = entry.artist,
            )

            db.session.add(new_song)
            db.session.commit()

            new_appearance = ChartAppearance(
                chart_id = new_chart.id,
                song_id = new_song.id,
                peak_pos = entry.peakPos,
                last_pos = entry.lastPos,
                weeks = entry.weeks,
                rank = entry.rank,
                isNew = entry.isNew,
                chart_date = new_chart.chart_date
            )

            db.session.add(new_appearance)
            db.session.commit()
    

    return redirect(f"/chart/{fetched_chart.date}")


def search():
    """ 
        Handles user-selected date requests.
        Passes dates to chart_search

        todo: handle date range validation

    """

    form = DateSearchForm()

    if form.validate_on_submit():
        inputted_date = form.date.data
        
        return redirect(f"/exists/{inputted_date}")
        
    return render_template("search.html", form=form)

def random_chart():
    
    earliest = datetime.date(1958, 8, 4)
    latest = datetime.date.today()
    
    random_days_between = random.randrange((latest-earliest).days)

    random_date = earliest + datetime.timedelta(days=random_days_between) 
    
    
    return redirect(f"/exists/{random_date}")