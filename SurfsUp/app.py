# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)
most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
latest_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
start_date = latest_date - dt.timedelta(days=365)
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Set up base route to display all available routes.
@app.route("/")
def welcome():
    return (
        f'Welcome to the API!<br/>'
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f'Stations: /api/v1.0/stations<br/>'
        f'TOBS: /api/v1.0/tobs<br/>'
        f'Temperatures at start date: /api/v1.0/temp/start<br/>'
        f'Terperatures at end date: /api/v1.0/temp/start/end<br/>'
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

# Convert the query results from your precipitation analysis (saved outside 
# loops up above) (i.e. retrieve only the last 12 months of data) to a dictionary 
# using date as the key and prcp as the value.
    precip = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= start_date).all()
    session.close()

# Return the JSON representation of your dictionary. Create an empty list to fill
# with the dictionary you create using a for loop on the results of the precip query.
# append use a 
    all_prcp = []
    for date, prcp  in precip:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
               
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

#################################################
# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def station():
    session = Session(engine)
# Query the stationID and name for all stations.
    stations_query = session.query(Station.station, Station.name).all()
    session.close()

# Use the same strategy as above for precipitation to create list to fill with
# dictionary.
    stations = []
    for station, name in stations_query:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        stations.append(station_dict)

    # Return the JSON representation of the list of stations
    return jsonify(stations)

#################################################
# Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

# Use the query generated in climate_starter.ipynb to get the most active stations and choose the most
# active below for your temp_data query
    active = session.query(Measurement.station, func.count(Measurement.id)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).all()

    station_no = active[0][0]

    temp_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == station_no).\
    filter(Measurement.date  >= start_date).all()
    session.close()

# Return a JSON list of temperature observations for the previous year.
    all_tobs = []
    for date, tobs in temp_data:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temp obs'] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#################################################
# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    if not end:
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates 
# greater than or equal to the start date (to be input by user). 
        session = Session(engine)
        start = dt.datetime.strptime(start, "%Y%m%d")
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        session.close()

# Unravel results and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

# identify the format for start and end dates    
    start = dt.datetime.strptime(start, "%Y%m%d")
    end = dt.datetime.strptime(end, "%Y%m%d")

# calculate TMIN, TAVG, TMAX with start and end dates (to be input by user).
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    # Unravel results and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)