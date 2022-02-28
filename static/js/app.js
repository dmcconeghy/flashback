console.log("JS is here.")



function turnPage(){
    leftTracks = document.getElementById('tracks-left')
    rightTracks = document.getElementById('tracks-right')

    leftTracksClick = document.getElementById('tracks-left-click')
    rightTracksClick = document.getElementById('tracks-right-click')
    
    leftTracksClick.addEventListener("click", (e) => {

        leftTracks.classList.add('tracks-animate-left')
        console.log("You clicked", e.currentTarget)
        console.log("CLicked the left container")
        setTimeout(() => leftTracks.classList.remove('tracks-animate-left'), 2000)
    }
    )

    rightTracksClick.addEventListener("click", (e) => {
 
        rightTracks.classList.add('tracks-animate-right')
        console.log("You clicked", e.currentTarget)
        console.log("CLicked the right container")
        setTimeout(() => rightTracks.classList.remove('tracks-animate-right'), 2000)
        }
        
    )

}

// Wait for the page to load before attaching the event listeners
// Only load turnPage if we're on the jukebox page.
window.onload = () => {
    if (document.getElementById('jukebox-tracks')) {
        turnPage();
    }
}

