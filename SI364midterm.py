###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import spotify_info

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/sfdigi_midterm12"
app.config['SECRET_KEY'] = 'unique and hard to guess string for my si364 midterm'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)



## Spotify API Set Up

spotify_key = spotify_info.api_key




######################################
######## HELPER Classes ########
######################################
class nonDBalbum():
	"""object representing one artist."""
	def __init__(self, album_dict={}):
		if 'name' in album_dict:
			self.name = album_dict['name']
		else:
			self.name = ""
		
		if 'artist' in album_dict:
			self.artist = album_dict['artist']
		else:
			self.artist = ""

		if 'id_code' in album_dict:
			self.id_code = album_dict['id_code']
		else:
			self.id_code = ""

		if "artist_id" in album_dict:
			self.artist_id = album_dict['artist_id']

	def show_name(self):
		return self.name

	def show_id(self):
		return self.id_code

	def show_artist(self):
		return self.artist

	def show_artist_id(self):
		return self.artist_id


	def __str__(self):
		return "%s is an album by %s" % (self.name, self.artist)




######################################
######## HELPER FXNS (If any) ########
######################################

def ArtistInfo(artist_name):
	headers ={"Accept": "application/json", "Authorization" : "Bearer " + spotify_key}
	params = { 'q': artist_name, 'type': 'artist'}
	artist_data = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params).json()
	id_code = artist_data['artists']['items'][0]['id']
	return {"id_code": id_code}


def ArtistDiscog(artist):
	headers ={"Authorization" : "Bearer " + spotify_key}
	artist_data = requests.get('https://api.spotify.com/v1/artists/' + artist + "/albums", headers=headers).json()
	albums = []
	discog = []
	for item in artist_data['items']:
		album_id = item['id']
		album_name = item['name']
		artist_id = item['artists'][0]['id']
		artist_name = item['artists'][0]['name']
		check = Album.query.filter_by(id=album_id).first()
		if not check:
			album = Album(name=album_name, id=album_id, artist_name=artist_name)
			db.session.add(album)
			db.session.commit()
			return True
	return False

##################
##### MODELS #####
##################

class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.String(256), primary_key=True) #artistid
    name = db.Column(db.String(265))
    albums = db.relationship('Owns', backref='Artist')

    def __repr__(self):
        return "Artist: {}---- Spotify ID: {}".format(self.name, self.id)

class Album(db.Model):
	__tablename__ = 'albums'
	id = db.Column(db.String(256), primary_key=True) #albumid
	name = db.Column(db.String(256))
	artist_name = db.Column(db.String(56)) #artistname
	artist = db.relationship('Owns', backref='Album')

	def __repr__(self):
		return "{} is an album by {}".format(self.name, self.artist_name)

class Owns(db.Model):
	__tablename__ = "owns"
	id = db.Column(db.String(), db.ForeignKey("artists.id"), primary_key=True)
	albums = db.Column(db.String(), db.ForeignKey('albums.id'))

###################
###### FORMS ######
###################

class ArtistForm(FlaskForm):
    artist = StringField("Please enter the name of an artist to search on Spotify.",validators=[Required()])
    submit = SubmitField('Submit')    



class AlbumForm(FlaskForm):
	album_artist = StringField("Please enter an artist's Spotify ID code.",validators=[Required()])
	submit = SubmitField('Submit')

	def validate_album_artist(self, field):
		try:
			albums = ArtistDiscog(field.data)
		except:
			raise ValidationError('Artist ID is not real! Copy & paste one from the artist list.')

#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/',  methods=['GET', 'POST'])
def home():
    form = ArtistForm(request.form)  # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    if form.validate_on_submit():
        artist_name = form.artist.data
        artist_dic = ArtistInfo(artist_name)
        artist_id = artist_dic['id_code']

        artist = Artist.query.filter_by(name = artist_name).first()
        if not artist:
        	artist = Artist(name = artist_name, id=artist_id)

        ##Query for does it exist!!

        	db.session.add(artist)
        	db.session.commit()
        	return redirect(url_for('all_names'))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Artist.query.all()
    return render_template('name_example.html',artists=names)

@app.route('/albums', methods=['GET', 'POST'])
def albums():
	form = AlbumForm(request.form)
	if form.validate_on_submit():
		artist = form.album_artist.data
		discog = ArtistDiscog(artist)
		if discog == True:
			return redirect(url_for("all_albums"))
	return render_template('albums.html', form=form)




@app.route('/album_results')
def all_albums():
	info=[]
	albums = Album.query.all()
	for a in albums:
		album_name = a.name
		artist = a.artist_name
		tup = (artist, album_name)
		info.append(tup)
	return render_template('album_results.html', info=info[-1])

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
	db.create_all()
	app.run(use_reloader=True, debug=True)