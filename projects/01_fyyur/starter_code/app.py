#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1024))
    # Relations
    # DONE: Genres is a n:m with venue, show is a 1:n with venue
    genres= db.Column(ARRAY(db.String()), nullable=False)
    shows = db.relationship('Show', backref='venues',
                            lazy=True, cascade="delete")

    def __repr__(self):
        return f'<Venue \
        {self.id}, \
        {self.name},\
        {self.city},\
        {self.state},\
        {self.address},\
        {self.phone},\
        {self.image_link},\
        {self.facebook_link},\
        {self.genres},\
        {self.website},\
        {self.seeking_talent},\
        {self.seeking_description}\
        >'


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres= db.Column(ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1024))
    shows = db.relationship('Show', backref='artists',
                            lazy=True, cascade="delete")
    def __repr__(self):
        return f'<Artist \
        {self.id}, \
        {self.name},\
        {self.city},\
        {self.shows}>'
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return f'<Show \
        {self.id}, \
        {self.venue_id},\
        {self.artist_id},\
        {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # Query for cities/states
    # foreach, query venues and display their upcoming shows
    city_areas = Venue.query.distinct('city', 'state').all()
    data = []
    for city_area in city_areas:
        venues_in_city = Venue.query.filter(
            Venue.city == city_area.city, Venue.state == city_area.state).all()
        entry = {
            'city': city_area.city,
            'state': city_area.state
        }
        venues = []
        for venue in venues_in_city:

            venueToAppend = {
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': Show.query.filter(Show.venue_id == venue.id,
              Show.start_time > datetime.utcnow()).count()
            }
            venues.append(venueToAppend)
            

        entry['venues'] = venues

        data.append(entry)
    


    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    #search venues 
    #venues = Venue.query.filter(Venue.name.contains(request.form.get('search_term'))).all()
    venues = Venue.query.filter(Venue.name.ilike('%'+request.form.get('search_term')+'%')).all()    
    response = {
        'count': len(venues),
        'data': venues
    }
  
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id);
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
    past_shows_query=db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    upcoming_shows=[]
    for show in upcoming_shows_query:
      upcoming_shows.append({
        "artist_id": show.artist_id,
          "artist_name": show.artists.name,
          "artist_image_link": show.artists.image_link,
          "start_time": show.start_time
      })
    past_shows=[]
    for show in past_shows_query:
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artists.name,
          "artist_image_link": show.artists.image_link,
          "start_time": show.start_time
        })
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "image_link": venue.image_link,
      "facebook_link": venue.facebook_link,
      "seeking_description": venue.seeking_description,
      "seeking_talent": venue.seeking_talent,
      "website": venue.website,
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows),
      "past_shows": past_shows,
      "past_shows_count": len(past_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    error = False
    form = VenueForm(request.form)
    try:
        venue = Venue(
            name = form.name.data,
            city = form.city.data,
            state = form.state.data,
            address = form.address.data,
            phone = form.phone.data,
            genres = form.genres.data,
            facebook_link = form.facebook_link.data)
        db.session.add(venue)
        db.session.commit()
    except ValueError:
        error=True
        db.session.rollback()
        print("Unexpected error", sys.exc_info())

    finally:
        db.session.close()
        # on successful db insert, flash success
    if error:
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
    else:
        flash('Venue ' + form.name.data + ' was successfully listed!')

    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods = ['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
      venueToDelete=Venue.query.get(venue_id)
      db.session.delete(venueToDelete)
      db.session.commit()
    except:
      error=True
      db.session.rollback()
      print("Unexpected error", sys.exc_info())
    finally:
      db.session.close()
    if error:
      abort (400)
    else:
      return redirect(url_for('index'))

    # NOT DONE: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists = Artist.query.all())


@app.route('/artists/search', methods = ['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_string = request.form.get('search_term')
    search = Artist.query.filter(Artist.name.ilike('%'+search_string+'%')).all()    
    response ={
        "count": len(search),
        "data": search
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term'))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
 
    # We take artist, past shows and upcoming ones from database
    artist = Artist.query.get(artist_id)
    print(artist.shows)
    past_shows_lambda = list(filter(lambda show: show.start_time < datetime.now(), artist.shows))
    upcoming_shows_lambda = list(filter(lambda show: show.start_time > datetime.now(), artist.shows))
   
    upcoming_shows=[]
    for show in upcoming_shows_lambda:
      upcoming_shows.append({
        "venue_id": show.venue_id,
          "venue_name": show.venues.name,
          "venue_image_link": show.venues.image_link,
          "start_time": show.start_time
      })

   
    past_shows=[]
    for past_show in past_shows_lambda:
   
      past_shows.append({
        "venue_id": past_show.venue_id,
          "venue_name": past_show.venues.name,
          "venue_image_link": past_show.venues.image_link,
          "start_time": past_show.start_time
      })
   
    
    past_shows_count = len(past_shows_lambda)
    upcoming_shows_count =len(upcoming_shows)
    data={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # DONE: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm(request.form)
    #Our form data
    try:
        artist = Artist.query.get(artist_id)
        form.populate_obj(artist)
        db.session.commit()    
    except:
        error = True
        print("Unexpected error", sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be edited.')
    else:
        flash('Artist ' + form.name.data + ' was successfully edited!')
    
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    
    # DONE: populate form with values from venue with ID <venue_id>
    venue=Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    try:
       venue = Venue.query.get(venue_id)
       form.populate_obj(venue)
       db.session.commit()
    except:
      
      db.session.rollback()
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
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    error = False
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data
        )
        db.session.add(artist)
        db.session.commit()
    except ValueError:
        error = True
        db.session.rollback()
        print("Unexpected error", sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
    else:
        flash('Artist ' + form.name.data + ' was successfully listed!')
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    allShows = Show.query.all()
    data=[]
    for show in allShows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venues.name,
            "artist_id": show.artist_id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time}
        )

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead
    form  = ShowForm(request.form)
    error = False  
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time= form.start_time.data
        )
        # artist = Artist.query.get(show.artist_id)
        # venue = Venue.query.get(show.venue_id)
        
        db.session.add(show)
        db.session.commit()
    except ValueError:
        error = True
        db.session.rollback()
        print("Unexpected error", sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error. Show could not be listed.')
    else:
        flash('Show was successfully listed!')
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., 
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
