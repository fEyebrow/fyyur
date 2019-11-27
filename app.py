#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from itertools import groupby
from datetime import datetime
from util import *
from models import Show, Venue, Artist, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
with app.app_context():
        db.create_all()
        
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  print('date',value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  # return babel.dates.format_datetime(date, format)
  return date

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
  venues = Venue.query.all()
  sortedreader = sorted(venues, key=lambda d: (d.state, d.city))

  groups = groupby(sortedreader, key=lambda d: (d.state, d.city))
  result = []
  for item in groups:
      temp = {}
      temp['state'] = item[0][0]
      temp['city'] = item[0][1]
      temp['venues'] = []
      for venue in item[1]:
          now = datetime.now()
          num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time>now).count()
          v = { "id": venue.id, "name": venue.name, "num_upcoming_shows": num_upcoming_shows }
          temp['venues'].append(v)
      result.append(temp)
  
  return render_template('pages/venues.html', areas=result);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  origin_data = Venue.query.filter(Venue.name.ilike('%'+ request.form['search_term']+ '%')).all()
  print('search', origin_data)
  response['count'] = len(origin_data)
  data = []
  for item in origin_data:
    temp = {}
    temp['id'] = item.id
    temp['name'] = item.name
    now = datetime.now()
    upcoming_shows = Show.query.filter(Show.venue_id==item.id, Show.start_time>now).all()
    temp['num_upcoming_shows'] = len(upcoming_shows)
    data.append(temp)

  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  now = datetime.now()
  past_shows_data = Show.query.filter(Show.venue_id==venue_id,Show.start_time<=now).all()
  upcoming_shows_data = Show.query.filter(Show.venue_id==venue_id,Show.start_time>now).all()
  past_shows = []
  upcoming_shows = []
  for show in past_shows_data:
    temp = {}
    artist = Artist.query.filter(Artist.id==show.artist_id).all()
    artist = artist[0]
    temp['artist_id'] = artist.id
    temp['artist_name'] = artist.name
    temp['artist_image_link'] = artist.image_link
    temp['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    past_shows.append(temp)
  
  for show in upcoming_shows_data:
    temp = {}
    artist = Artist.query.filter(Artist.id==show.artist_id).all()
    artist = artist[0]
    temp['artist_id'] = artist.id
    temp['artist_name'] = artist.name
    temp['artist_image_link'] = artist.image_link
    temp['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    upcoming_shows.append(temp)
  
  venue.past_shows = past_shows
  venue.upcoming_shows = upcoming_shows
  venue.past_shows_count = len(past_shows)
  venue.upcoming_shows_count = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name')
    genres = request.form.getlist('genres')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    
    venur = Venue(name=name,genres=genres,address=address,city=city,state=state,phone=phone,facebook_link=facebook_link)
    db.session.add(venur)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    flash('fail to delete')
  else:
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  response = {}
  origin_data = Artist.query.filter(Artist.name.ilike('%'+ request.form['search_term']+ '%')).all()
  response['count'] = len(origin_data)
  data = []
  for item in origin_data:
    temp = {}
    temp['id'] = item.id
    temp['name'] = item.name
    now = datetime.now()
    upcoming_shows = Show.query.filter(Show.artist_id==item.id, Show.start_time>now).all()
    temp['num_upcoming_shows'] = len(upcoming_shows)
    data.append(temp)

  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.get(artist_id)
  print(type(data.genres)) 
  if type(data.genres) == str:
    data.genres = str2list(data.genres)
  
  now = datetime.now()
  past_shows_data = Show.query.filter(Show.artist_id==data.id,Show.start_time<=now).all()
  upcoming_shows_data = Show.query.filter(Show.artist_id==data.id,Show.start_time>now).all()
  past_shows = []
  for s in past_shows_data:
    temp = {}
    venue = Venue.query.get(s.venue_id)
    temp['venue_id'] = s.venue_id
    temp['venue_name'] = venue.name
    temp['venue_image_link'] = venue.image_link
    temp['start_time'] = s.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    past_shows.append(temp)

  upcoming_shows = []
  for s in upcoming_shows_data:
    temp = {}
    venue = Venue.query.get(s.venue_id)
    temp['venue_id'] = s.venue_id
    temp['venue_name'] = venue.name
    temp['venue_image_link'] = venue.image_link
    temp['start_time'] = s.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    upcoming_shows.append(temp)
  
  data.past_shows = past_shows
  data.upcoming_shows = upcoming_shows
  data.past_shows_count = len(past_shows)
  data.upcoming_shows_count = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  try:
    name = request.form['name']
    genres = request.form.getlist('genres')
    print('genres',genres)
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']

    artist = Artist(name=name,genres=genres,city=city,state=state,phone=phone,facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    abort(500)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    show.venue_name = venue.name
    show.artist_name = artist.name
    show.artist_image_link = artist.image_link
    show.start_time = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
  
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']

    show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    venue = Venue.query.get(venue_id)
    artist = Artist.query.get(artist_id)
    show.venue = venue
    show.artist = artist
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Show could not be listed.')
    abort(500)

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
