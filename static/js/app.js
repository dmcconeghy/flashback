console.log("JS is here.")

function turnPage(){
    leftTracks = document.getElementById('tracks-left')
    rightTracks = document.getElementById('tracks-right')
    
    leftTracks.addEventListener("click", (e) => {

        leftTracks.classList.add('tracks-animate-left')
        console.log("You clicked", e.currentTarget)
        console.log("CLicked the left container")
        setTimeout(() => leftTracks.classList.remove('tracks-animate-left'), 2000)
    }
    )

    rightTracks.addEventListener("click", (e) => {

        
        rightTracks.classList.add('tracks-animate-right')
        console.log("You clicked", e.currentTarget)
        console.log("CLicked the right container")
        setTimeout(() => rightTracks.classList.remove('tracks-animate-right'), 2000)
        }
        
    )

}

turnPage()