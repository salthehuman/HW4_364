# Si 364 Midterm Project
# By Salvatore DiGioia

# Background:

# This application uses the Spotify API to retrieve information about individual artists that have been input by the user. To do so, it 
# searches their name, retrieves the unique Spotify ID code associated with each name, then searches this ID code for two different types # of data -- albums + songs.
#


# Instructions

# Before running this application, the user must retireve a Spotify API Key (from here: )
# The user must then open the Python file called "spotify_info" & replace the current key with their new one.

# In order to run this app, one simply has to type in the name of an artist that is recognized by Spotify. The user will then be 
# re-directed to a page that shows the name of the most recenlt album on which their artist appears. On the same page, the user
# will be prompted to click a link that leads to that artist's top songs. This list of songs is retrieved via seperate get request
# to the Spotify API and directs the user to an entirely seperate view function. 



# Pre-Cautionaries 

# Error handlers do not explain themselves. Should a user search an artist that is already existent in the database, the request will not 
# go through, and the page will not change. This is the reason.

# Should a user be searching for an artist who shares the same name with a more popular artist, the more popular artist will automatically # be chosen by the program.