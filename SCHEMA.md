For this project there are three primary models -- users, songs, and charts. Users resembles other such instances -- username, password, email, etc. Songs & charts are the endpoints for searches. A user will either ask for a specific song or use a date to retrieve a particular chart. Implementation of the date endpoint is the primary goal, and searches for specific songs is the stretch goal for this version of the project. 

Charts map data from [guoguo12's billboard.py API](https://github.com/guoguo12/billboard-charts).

A chart retrieval is straightforward -- a correctly formatted date will return a chart instance. Each instance contains entries that list track/song data such as the title and artists. These data points will then be mapped to our song model. Saving the chart reduces further calls for that date's endpoint, but we don't want the song data buried within the chart model. Creating a relationship and using a combined key field helps us separate a chart's songs into individual database rows. It also reduces duplication since charts are singular (e.g. a single week, month or year) while songs are multiple -- they can appear in numerous charts.   

Songs contains a much larger number of fields. They combine Billboard data with additional requests to the iTunes API for information Billboard omits such as the name of the album a particular song appeared on or when it was initially released. These calls go to the iTunes.searchMusic endpoint (limited to 20/min?). [More details here](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/) 

Since each call to Charts returns all 100 of a specific chart's entries, we begin with a large volume of initial data and will likely need to choose which songs to fetch additional data for (perhaps by lazy loading the calls). The UI/UX will make a difference here, since displaying the data differently could make a notable change in how much of the data needs to be retrieved at once. iTunes calls for any individual song only need to be completed once -- no matter how many times that song appears in different charts. Different kinds of charts ('Hot 100', 'Global', etc.) complicate this somewhat, and in the first version of this app it will be necessary to limit searches to a single chart type "Hot 100" since the Global 200 chart is albumns only. 

After searching for a particular chart, a user might wish to save particular songs to their "favorites" list, which will give a use homepage a bulk of useful data to display. An additional stretch goal might be to let users play clips of the songs using the iTunes API or to export the song lists to Spotify. Or to show music videos using the YouTube API.

Song retrieval is more complex. First, a search endpoint needs to correctly identify a track. For this we will need to start with the iTunes API instead and use its superior logic handling to return the likeliest result. Once we have a track_id, then we can identify the songs release date and begin to query subsequent weeks on the Billboard API to look for matches using the artist name and song title. Checking the yearly charts may be a fast first check, though this only succeeds if the song in question was a big hit. Combined with a release date we will have a much narrower window of weeks to search. If we find any instance of a song's appearance, its chart entry tells us everything we need to know in order to find all its appearances (i.e., songs.weeks). 

Billboard does NOT have a search endpoint for specific songs or artists. (This is one strong argument in favor of simply downloading the entire billboard Chart data so that it can be queried in this way.)



![schema diagram](/Flashback%20Data%20Schema.jpeg)

