# flashback

### A musical memory project by Dave McConeghy
[Connect with me on LinkedIn](https://www.linkedin.com/in/david-mcconeghy/)

Flaskback is a capstone project I completed for Springboard's Software Engineering Career Track Fullstack Bootcamp.

Users can explore any Billboard Hot 100 chart since 1958 and save their favorite songs to their user profile. 

It features full CRUD for users, and relies on the [billboard-charts API](https://github.com/guoguo12/billboard-charts) to populate a Postgresql backend coded with Python, Flask, and Flask-SQLAlchemy. 

Database population is performed upon first request, with massive reductions in load times for subsequent calls to the same chart endpoint and signficant reductions in load times for chronologically adjacent charts (i.e., querying 2000-1-7 reduces load times for calls to 2000-01-01 and 2000-01-15).  

[Site is currently deployed at https://flashback-dwm.herokuapp.com/](https://flashback-dwm.herokuapp.com/) 


### Original Proposal by Dave McConeghy
Feel free to check out my initial proposal. 
[View this proposal in Google Docs](https://docs.google.com/document/d/1gXzn_mwFInoAnlA48n6XPhq4FItoeB0_nv4R6NYPp1A/edit?usp=sharing)



