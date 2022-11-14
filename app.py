#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import logging
import sys
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from sqlalchemy.sql import func,expression
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(200))
    genres = db.Column(db.ARRAY(db.String(120)))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))

class Show(db.Model):
    __tablename__ = 'Show'
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  places  = db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state)
  data = []
  for place in places:
    res = {}
    res['city'] = place.city
    res['state'] = place.state
    venues  = Venue.query.filter_by(city = place.city,state=place.state).all()
    for venue in venues:
      num_upcoming_shows = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time >= datetime.today()).count()
      res['venues'] = [{ 'id' : venue.id, 
                          'name' : venue.name,
                          "num_upcoming_shows": num_upcoming_shows
                      }]
    data.append(res)
  db.session.close()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchTerm= request.form.get('search_term')
  query = db.session.query(Venue).filter(func.lower(Venue.name).contains(func.lower(expression.literal(searchTerm)))).all()
  query_count = len(query)
  response={
    "count": query_count,
    "data": query
  }
  return render_template('pages/search_venues.html', results=response, search_term=searchTerm)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  #  query venue
  venue  = Venue.query.filter_by(id = venue_id).first()
  # get upcoming shows with venue_id
  upcoming_shows = db.session.query(Artist.id.label('artist_id'),
                               Artist.name.label('artist_name'),
                               Artist.image_link.label('artist_image_link'),
                               func.to_char(Show.start_time,"YYYY-mm-dd HH:MM:SS").label('start_time')
                               ).join(Show, Show.artist_id == Artist.id
                                ).join(Venue, Show.venue_id == Venue.id,
                                  ).filter(Venue.id == venue_id, Show.start_time >= datetime.today()).all()

  setattr(venue,'upcoming_shows',upcoming_shows)
  # get past shows with venue_id
  past_shows = db.session.query(Artist.id.label('artist_id'),
                               Artist.name.label('artist_name'),
                               Artist.image_link.label('artist_image_link'),
                               func.to_char(Show.start_time,"YYYY-mm-dd HH:MM:SS").label('start_time')
                               ).join(Show, Show.artist_id == Artist.id
                                ).join(Venue, Show.venue_id == Venue.id,
                                  ).filter(Venue.id == venue_id, Show.start_time < datetime.today()).all()
  setattr(venue,'past_shows',past_shows)
  setattr(venue,'past_shows_count',len(past_shows))
  setattr(venue,'upcoming_shows_count',len(upcoming_shows))

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    venue = Venue(name= request.form['name'],city= request.form['city'],state= request.form['state'],address= request.form['address'],phone= request.form['phone'],genres= request.form.getlist('genres'),facebook_link= request.form['facebook_link'],image_link= request.form['image_link'],website= request.form['website_link'],seeking_talent= request.form['seeking_talent'] == 'y' ,seeking_description = request.form['seeking_description'])
    db.session.add(venue)
    db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()

  # on successful db insert, flash success\
  print( request.form.getlist('genres'))
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The Venue has been successfully deleted!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('Delete was unsuccessful. Try again!')
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  searchTerm= request.form.get('search_term')
  query = Artist.query().filter(func.lower(Artist.name).contains(func.lower(func.literal(searchTerm)))).all()
  query_count = len(query)
  response={
    "count": query_count,
    "data": query
  }
  return render_template('pages/search_artists.html', results=response, search_term=searchTerm)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist  = Artist.query.filter_by(id = artist_id).first()
    # get upcoming shows with venue_id
  upcoming_shows = db.session.query(Venue.id.label('venue_id'),
                               Venue.name.label('venue_name'),
                               Venue.image_link.label('venue_image_link'),
                               func.to_char(Show.start_time,"YYYY-mm-dd HH:MM:SS").label('start_time')
                               ).join(Show, Show.venue_id == Venue.id
                                ).join(Artist, Show.venue_id == Artist.id,
                                  ).filter(Artist.id == artist_id, Show.start_time >= datetime.today()).all()

  setattr(artist,'upcoming_shows',upcoming_shows)
  # get past shows with venue_id
  past_shows = db.session.query(Venue.id.label('venue_id'),
                               Venue.name.label('venue_name'),
                               Venue.image_link.label('venue_image_link'),
                               func.to_char(Show.start_time,"YYYY-mm-dd HH:MM:SS").label('start_time')
                               ).join(Show, Show.venue_id == Venue.id
                                ).join(Artist, Show.artist_id == Artist.id,
                                  ).filter(Artist.id == artist_id, Show.start_time < datetime.today()).all()
  setattr(artist,'past_shows',past_shows)
  setattr(artist,'past_shows_count',len(past_shows))
  setattr(artist,'upcoming_shows_count',len(upcoming_shows))
  form = ArtistForm()
  return render_template('pages/show_artist.html',form=form, artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist  = Artist.query.get(artist_id)
  form = ArtistForm()
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # query artist with id
  artist  = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form.getlist('genres')
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.seeking_description = request.form['seeking_description']
    artist.seeking_venue = request.form['seeking_venue'] == 'y'
    artist.state =request.form['state']
    artist.website = request.form['website_link']
    db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue  = Venue.query.filter_by(id = venue_id).first()
  form = VenueForm()
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #  query venue with id
  venue  = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.phone = request.form['phone']
    venue.seeking_description = request.form['seeking_description']
    venue.seeking_talent = request.form['seeking_talent'] == 'y'
    venue.website = request.form['website_link']
    db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close() 
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist = Artist(name = request.form['name'],city= request.form['city'],state= request.form['state'],phone= request.form['phone'],genres= request.form.getlist('genres'),facebook_link= request.form['facebook_link'],image_link= request.form['image_link'],website= request.form['website_link'],seeking_venue= request.form['seeking_venue'] == 'y' ,seeking_description = request.form['seeking_description'])

    db.session.add(artist)
    db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = db.session.query(Artist.id.label('artist_id'),
                          Artist.name.label('artist_name'),
                          Artist.image_link.label('artist_image_link'),
                          Venue.id.label('venue_id'),
                          Venue.name.label('artist_name'),
                          func.to_char(Show.start_time,"YYYY-mm-dd HH:MM:SS").label('start_time')).join(Show, Show.artist_id == Artist.id).join(Venue, Show.venue_id == Venue.id).all()
  db.session.close()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(start_time= request.form['start_time'],venue_id= request.form['venue_id'],artist_id= request.form['artist_id'])

    db.session.add(show)
    db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
      
  finally:
      db.session.close()
  flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
