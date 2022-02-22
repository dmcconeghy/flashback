# flashback

### A musical memory project by Dave McConeghy

Project completed for Springboard Software Engineering Career Track Fullstack Bootcamp

https://www.linkedin.com/in/david-mcconeghy/

***


The initial pitch was: 

>Ever have a moment when you hear a song and it brings you back to the first time you heard it? Can’t remember how old you were or what else was going on back then? No problem. Enter your birthdate and a song and Flashback will tell you how old you were when that song was released or charted on Billboard’s Hot 100 and give you basic information about that song (who recorded it, what album it was on, etc.).
>   
> - Combines “how old was I on x date” and “What happened on x date” apps like thisdayinmusic, onthisday, or past age calculator with song
> 
> - Likely APIs: Billboard-charts/Wikipedia (for date-based track popularity information) and Spotify/iTunes (for track metadata). 

*** 

My initial proposal (following a proposal template) was: 

## Flashback: A Music Memory Project

## Springboard Capstone I Proposal by Dave McConeghy
[View this proposal in Google Docs](https://docs.google.com/document/d/1gXzn_mwFInoAnlA48n6XPhq4FItoeB0_nv4R6NYPp1A/edit?usp=sharing)

### Overview:

>Ever have a moment when you hear a song and it brings you back to the first time you heard it? Can’t remember how old you were or what else was going on back then? No problem. Enter a date or a song and Flashback will tell when that song was released or charted on Billboard’s Hot 100 and give you basic information about that song (who recorded it, what album it was on, etc.)

### Goal: 

Using a date or song, Flashback will show users a timeline with the immediate musical context for their chosen date or song. Enter January 1995 and you’ll see that Boyz II Men’s “On Bended Knee” was #1 in the US. Enter “Gangsta’s Paradise” and you’ll see that Coolio’s hit charted #1 in September of 1995. 

For context, users will see other songs from that moment’s Billboard chart and details about songs such as their album, lyrics, or release date. With user provided data, the results can include details such as “how old was I” or limit/filter results to a preferred genre. 

Users should be able to listen to the songs without leaving the app and, if applicable, save the songs to a custom playlist in a user’s spotify account.

### Demographics:

This app will be of interest to anyone old enough to have forgotten when they first heard a piece of popular music. Or, alternatively, someone young enough to have missed the release of an older piece of music and curious about what else was happening musically during that era. At an upper limit this means anyone who listens to or enjoys music and might enjoy exploring music in a chronological way. 

### Data Use:

Flashback requires several APIs in order to serve users data such as a song’s artist, album, release date, audio/video link, and Billboard chart record. The complete Billboard data has been scraped by others so that Flashback could use an internal server side API, but there is also a standalone API to pull specific data as well as the option to retrieve or scrape this data from Wikipedia. 

- First, given any date, the app must use Billboard data to retrieve the list of songs charting at that time, their artists, album art, and data about their position on the Billboard charts. Then for each song we will need release date, genre, and album data. These are not included in the Billboard data, but can be fetched using the iTunes API. 

- Second, given any song, the app must search for a song match using the iTunes API and return an artist/song ID which can then be used to return additional data about its release date, genre, and album. Next, the song can be passed into the Billboard API to return its chart position.

- Third, to play any given song, we will need to either authenticate a user with their pre-existing Spotify account or serve the user an alternative (say from YouTube). 

- Fourth, if an authenticated Spotify user wishes to save a song to their playlist, the app will need to correctly use the Spotify playlist endpoints. 

### Project Outline:

- Data Schema #1: Much like the Database DJ project this project is well served by a songs > playlist songs < playlists structure. In this instance we have a db of songs and we want them to be shown as a (play)list (weekly chart instance). So each week’s Billboard chart is a playlist and the playlist songs contain the combined playlist_id and song_id. Songs will closely resemble the raw Billboard data, since each row of that db contains all the pre-existing song data we need such:
  
    - Billboard Chart URL
    - WeekID [This = playlist above]
    - Song name
    - Performer name
    - SongID - Concatenation of song & performer
    - Current week on chart
    - Instance (this is used to separate breaks on the chart for a given song. Example, an instance of 6 tells you that this is the sixth time this song has appeared on the chart)
    - Previous week position
    - Peak Position (as of the corresponding week)
    - Weeks on Chart (as of the corresponding week)
     
- Data Schema #2: None of #1 above necessarily requires CRUD. If we serve data through our own API calls to a locally held copy of Billboard data, it also doesn’t need an external API. Since both aspects are part of this project… 
    - Flashback should supplement Billboard data with calls to Spotify, iTunes and/or Genius(for lyrics). iTunes is a great choice for obtaining album art, release details, and several other data points. Additionally, the Billboard data has a parallel db with each song’s Spotify track data. This is a HUGE call saver for basic data calls such as the song’s Spotify ID. This will allow Flashback to easily export playlists to Spotify. 
    - We will also need a user schema that can hold those playlists and allow for authentication. This will also likely mean a custom playlist schema containing a list of song ids. Users will need:
         - User ID
         - Username
         - Password
         - Email
         - DOB (optional)
         - Spotify authentication (optional)
         - //Bookmarked songs (separate table?)
         - //Custom playlist IDs

### Potential issues:

Using an external API for Billboard data will generate a huge number of calls. While the API can be forked (and it really is just a web scrape of the Billboard charts), it’s likely better to make an internal server-side API for the downloaded Billboard chart data. 
Over-relying on Spotify carries risks of running into call limits. 100/day could easily be hit by creating just a handful of playlists or browsing the timeline for a few minutes (since each song might include an option to listen through spotify).

ITunes will be doing some heavier lifting thanks to its generous API limits, but that comes with limitations such as limited metadata that could be used for suggesting other similar songs. If the site were to be continued live, the option to purchase the songs through Apple seems like an obvious add-on.

### Sensitive data:
Yes. Users with passwords. Spotify authentication details. DOB.

### Basic App functionality: 
- Date look up (returns chart from particular day/week). 
- Song look up (returns chart for that song’s release/appearance).
- Timeline Chart browsing (moves users back or forward in time showing other charts, probably just the first 10 items). 
- Timeline Song browsing (like chart but timeline is for other chronologically close songs that charted or were released then).
- Detailed song description(A modal(?) to display a particular song’s data.) 
- User log in & Spotify authentication. 
- User playlist saving (Bookmarks songs and saves them to a user’s profile.)
- Spotify playlist upload (with buttons to do this in timeline browsing or from a song’s detail page).
   
### User Flow: 

Users will arrive at the site and see an initial enter date / enter a song choice. Entering either will bring users results showing that date’s chart or that song’s details. Users can then a) explore other songs they see in the results or b) charts where that song appears or c) chronologically related charts (e.g., week before/ week after). These items will have buttons that if clicked and no logged in user is found will then prompt the user to create an account or log in. Logging in then generates the option to save those items to a user’s profile. Logged in users can access a profile page where their bookmarked songs are list and can be added to custom playlists to send to spotify.

### Stretch Goals: 

This is already a lot, but one feature that would be unique would be to add the option for users to annotate a song with their memories about it. This could be used as an exploration hook in the landing page (sort of like customer testimonials?). Another option would be to allow for YouTube videos as a replacement/supplement to playing the songs through a verified Spotify (or Apple music?) account. I think there’s a lot more than simple CRUD here. In fact, it’s a lot of non-crud with CRUD used as a framework to save non-Crud exploration. 
