# Import dependices
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Flask Routes

@app.route("/")
def homepage():
    """List of all available routes""" 
    return (
        f"Welcome!<br/><br/>"
        f"Note: dates only range from 2010-01-01 to 2017-08-23<br/><br/><br/>"

        f"Available Routes:<br/><br/>"

        f"/api/v1.0/precipitation<br/>"
        f"Returns a list of dates and amounts of precipitation.<br/><br/>"

        f"/api/v1.0/stations<br/>"
        f"Returns a list of stations.<br/><br/>"

        f"/api/v1.0/tobs<br/>"
        f"Returns a list of temperature observations from the previous year.<br/><br/>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"Returns a minimum, average, and maximum temperature for a given start date (yyyy-mm-dd).<br/><br/>"
    
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"Returns a minimum, average, and maximum temperature for given date range (yyyy-mm-dd)."
    )

#Precipitation page
@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create session
    session = Session(engine)
    """Return a list of date and precipitation"""
    # Query results
    results = session.query(Measurement.date, Measurement.prcp, Measurement.station).order_by(Measurement.date.desc()).all()
    # Close session
    session.close()
    # Create a dictionary
    all_prcps = []
    for date, prcp, station in results:
        precip_dict = {}
        precip_dict["key"] = date
        precip_dict["value"] = prcp
        precip_dict["station"] = station
        all_prcps.append(precip_dict)
    #Convert to JSON
    return jsonify(all_prcps)

# Stations page
@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)
    """Return station data"""
    #Query results
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()
    #Close session
    session.close()
    # Create dictionary
    all_stations = []
    for result in results:
        station_dict = {}
        station_dict["Station ID"] = result[0]
        station_dict["Name"] = result[1]
        station_dict["Latitude"] = result[2]
        station_dict["Longitude"] = result[3]
        station_dict["Elevation"] = result[4]
        all_stations.append(station_dict)
    #Convert to JSON
    return jsonify(all_stations)

# Tobs page
@app.route("/api/v1.0/tobs")
def tobs():
    # Session start, query, and close
    session = Session(engine)
    """Return a list of date and temperature observations"""
    sel = [Measurement.date, Measurement.tobs, Measurement.station]
    results = session.query(*sel).filter(Measurement.date >='2016-08-23', Measurement.date <= '2017-08-23').order_by(Measurement.date.desc()).all()
    session.close()
    # Create dictionary
    all_tobs = []
    for date,tob,station in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["TOB"] = tob
        tobs_dict["Station"] = station
        all_tobs.append(tobs_dict)
    # Convert to JSON
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start_date>/")
def data_start_date(start_date):
    # Session start, query, and close
    session = Session(engine)
    """Return temp data for start date"""
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).group_by(Measurement.date).order_by(Measurement.date).all()
    session.close()
    # Create dictionary
    start_temps = []
    for result in results:
        start_dict = {}
        start_dict["Date"] = result[0]
        start_dict["Minimum"] = result[1]
        start_dict["Average"] = result[2]
        start_dict["Maximum"] = result[3]
        start_temps.append(start_dict)
    # Convert to JSON
    return jsonify(start_temps)


@app.route("/api/v1.0/<start_date>/<end_date>")
def data_start_end(start_date, end_date):
    # Session start, query, and close
    session = Session(engine)
    """Return temp data for date range"""
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).group_by(Measurement.date).order_by(Measurement.date).all()
    session.close()
    # Create dictionary
    start_end_temps = []
    for result in results:
        start_end_dict = {}
        start_end_dict["Date"] = result[0]
        start_end_dict["Minimum"] = result[1]
        start_end_dict["Average"] = result[2]
        start_end_dict["Maximum"] = result[3]
        start_end_temps.append(start_end_dict)
    # Convert to JSON
    return jsonify(start_end_temps)

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

