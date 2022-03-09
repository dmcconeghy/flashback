from flask import render_template
from models import Chart, Song, ChartAppearance


################### CHARTS ################### 
# @app.route('/charts', methods=['GET', 'POST'])
def show_list_of_charts():
    """ This route returns a list of database stored charts 
    
    
    ChartAppearance.chart_date == chart.chart_date.isoformat()

    ATM, this route's returns /charts results out of order.
    The five items shown in charts.html are NOT that chart date's top 5 songs (by clicking through to chart/<date>).
    Is this because of the initial state of the chart relationship for items that already exist in Song? 
    """

    charts = Chart.query.order_by(Chart.chart_date.desc()).all()
    
    chart_list = []

    for chart in charts:
        chart_date = chart.chart_date.isoformat()

        song_ids = [s.song_id for s in chart.songs]
        appearance_objects = [a for a in chart.songs]

        # sort the list of appearances by their ranks
        appearance_objects.sort(key=lambda x: x.rank)

        song_objects = [Song.query.get(sid) for sid in song_ids]

        #                 
        # song_objects = [(Song
        #                 .query
        #                 .join(ChartAppearance, ChartAppearance.song_id == sid)
        #                 .filter(ChartAppearance.chart_date == chart_date)
        #                 .order_by(ChartAppearance.rank)
        #                 .all()
        #                 ) for sid in song_ids]


        chart_merge = zip(song_objects, appearance_objects)
        chart_list.append(chart_merge)

    return render_template('charts.html', charts=charts, results=chart_list)

# @app.route('/chart/<string:req_chart_date>', methods=['GET', 'POST'])
def show_chart(req_chart_date):
    """ 
        Display a specific chart and its songs

        This route must occur AFTER validation through exists.

        todo: fix issues with duplicate entries cf. "Unchained Melody" from 10.06.90 - 3.23.91
            There are two version on this chart but they're indistinguishable in single API data calls.
            The original peaked at #4 in 08.28.65 but *also* charted in 1990. 
            Presently, each duplicate entry adds a new Song entry, which isn't ideal. 
            There are likely many other such re-charts and duplication oddities to handle. 

    """

    chart = Chart.query.filter(Chart.chart_date == req_chart_date).first()

    appearances = (
        ChartAppearance
        .query
        .join(Song, ChartAppearance.song_id == Song.id)
        .filter(ChartAppearance.chart_date == req_chart_date)
        .order_by(ChartAppearance.rank)
        .all()
        )

    songs = (
        Song
        .query
        .join(ChartAppearance, Song.id == ChartAppearance.song_id)
        .filter(ChartAppearance.chart_date == req_chart_date)
        .all()
        )

    return render_template('chart_results.html', chart=chart, results=zip(songs, appearances))
