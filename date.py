# def convert_to_datetime(chart_date):
    #     datetime_object = datetime.datetime.fromisoformat(chart_date)
    #     return datetime_object

    # def previously_fetched(validated_date):
    #     """ 
    #     Does our chart date exist already? 
    #     Yes? Return db version.
    #     No? Fetch it. 
    #     """
        
    #     found_chart = (Chart
    #                 .query
    #                 .filter(Chart.chart_date == validated_date)
    #                 .all()) 

    #     if found_chart:
    #         return True
    #     else:
    #         return False

    # def validate_date(user_inputted_date):
    #     """ 
    #         Given the user inputted date, find the closest billboard chart.

    #         Users input dates in the format YYYY-MM-DD. 
    #         We grab the value of the day in its week (0-6).

    #         Then we convert the inputted date to its Gregorian ordinal. 
    #         Next we adjust the ordinal to find the closest tuesday using day_validator. 
    #         Finally we return the date in the original format 
        
    #         Charts are released on Tuesdays but post-dated for the following Saturday.

    #         While the API performs a similar calculation, we want to pre-exmptively exclude using it if we've already fetched that chart. 
    #         So we must identify the date that the API *would* return and look for that first.  
        
    #     """
        
    #     weekday = datetime.date.weekday(user_inputted_date)

    #     day_validator = {
    #         '0' : -2,
    #         '1' : -3,
    #         '2' : 3,
    #         '3' : 2,
    #         '4' : 1,
    #         '5' : 0,
    #         '6' : -1
    #     }

    #     adjustment = day_validator.get(str(weekday))

    #     date_as_ordinal = datetime.date.toordinal(user_inputted_date)

    #     closest_saturday = date_as_ordinal + adjustment

    #     return datetime.date.fromordinal(closest_saturday)

    # datetime_date = convert_to_datetime(chart_date)
    # valid_date = validate_date(datetime_date)

    # for chart in charts:

    #     appearances = (
    #         ChartAppearance
    #         .query
    #         .join(Song, ChartAppearance.song_id == Song.id)
    #         .filter(ChartAppearance.chart_date == chart.chart_date.isoformat())
    #         .order_by(ChartAppearance.rank)  
    #         .all()
    #         )

    #     songs = (
    #         Song
    #         .query
    #         .join(ChartAppearance, Song.id == ChartAppearance.song_id)
    #         .filter(ChartAppearance.chart_date == chart.chart_date.isoformat())
    #         .limit(10)
    #         .all()
    #         )
    # results=zip(appearances, songs)

    # songs = (Chart
    #             .query
    #             .join(ChartAppearance, ChartAppearance.chart_id == Chart.id)
    #             .join(Song, ChartAppearance.song_id == Song.id)
    #             .filter(ChartAppearance.rank == 1)
    #             .order_by(ChartAppearance.chart_date.desc())
    #             .value(Song.title, Song.artist)
    #             .all()
    #         )
        
    # songs = (Song
    #         .query
    #         .join(ChartAppearance, Song.id == ChartAppearance.song_id)
    #         .join(Chart, ChartAppearance.chart_id == Chart.id)
    #         .filter(ChartAppearance.rank == 1)
    #         .order_by(ChartAppearance.chart_date.desc())
    #         .all())
    # results = zip(songs, charts)