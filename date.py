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

# song_ids = [s.song_id for s in chart.songs]
        # appearance_objects = [a for a in chart.songs]

        # sort the list of appearances by their ranks
        # appearance_objects.sort(key=lambda x: x.rank)

#                 
        # song_objects = [(Song
        #                 .query
        #                 .join(ChartAppearance, ChartAppearance.song_id == sid)
        #                 .filter(ChartAppearance.chart_date == chart_date)
        #                 .order_by(ChartAppearance.rank)
        #                 .all()
        #                 ) for sid in song_ids]

# chart_date = chart.chart_date.isoformat()

# response = Song.query.order_by(Song.id).all()

    # for song in all_songs:
    #     # Check if artist page has been searched for
    #     if song.artist_page == "Not Queried":
            
    #         # Check if artist page search turned up empty
    #         if song.find_artist_page() != False:
                
    #             # Search for an image
    #             song.get_artist_image()


#     {% extends 'base.html' %}

# {% block title %} TEST {% endblock %}


# {% block content %} 
# <div class="container-fluid col-lg-6">
# 	<div class="row bg-info">
# 		<div class="col-md-9"> THIS WEEK {{chart.date}}
# 		</div>
# 		<div class="col-md-1"> LAST WEEK
# 		</div>
# 		<div class="col-md-1"> PEAK POSITION
# 		</div>
# 		<div class="col-md-1"> WEEKS ON CHART
# 		</div>
# 	</div>
        
#     {% for entry in chart %}
    
#         <div class="row">
#             <div class="col-md-1 text-center align-middle"> {{entry.rank}}
#             </div>
#             <div class="col-md-1 text-center align-middle">
#                 <img class="img-fluid" src="../static/media/missing_album_art.svg" alt="default album image">
#             </div>
#             <div class="col-md-7 text-left align-middle">
#                 {{entry.title | truncate(25) }} by {{entry.artist | truncate(30) }}
#             </div>
#             <div class="col-md-1 text-center"> {{entry.lastPos}}
#             </div>
#             <div class="col-md-1 text-center">{{entry.peakPos}}
#             </div>
#             <div class="col-md-1 text-center">{{entry.weeks}}
#             </div>
#         </div>
        
#     {% endfor %}
# </div>

# {% endblock %}

# <!-- <li>
                    
#                     {{entry.title}} by {{entry.artist}}
                    
#                 </li> -->

#                 <!-- <div class="card" style="width: 18rem">
#                     <img src="{{ entry.image }}" class="card-img-top" alt=""/>
#                     <div class="div card-body">
#                         <img class="card-image" src="../static/media/musical_placeholder.jpg">
#                         <h5 class="card-title">{{entry.rank}}:{{entry.title}} by {{entry.artist|truncate(20)}}</h5>
#                         <p class="card-text">Highest position: {{entry.peakPos}} </p>
#                         <p class="card-text">{{entry.weeks}} weeks on chart</p>
                        
#                     </div>
#                 </div> -->

