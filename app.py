# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base=automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

# Flask setup
from flask import Flask, jsonify
app = Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    """Return all routes"""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"For precipitation data for the previous year:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>" 
        f"For a list of weather stations:<br/>" 
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"For temperature observations from station USC00519281<br/>"  
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For descriptive stats by date, please replace<br/>"
        f"the placeholder date with the desired date :<br/>" 
        f"/api/v1.0/temp/2016-08-23<br/>"
        f"<br/>"
        f"For descriptive stats by range please replace<br/>" 
        f"the placeholder dates with the desired dates :<br/>" 
        f"/api/v1.0/temp/2016-08-23/2017-08-23<br/>"
    )
    
# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data including the date and prcp"""
    # Starting from the most recent data point in the database.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year_ago = most_recent_date - dt.timedelta(days=365)  

    # Perform a query to retrieve the data and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    precipitation=[]
    for result in query:
        precipitation_dict={}
        precipitation_dict["date"]=result.date
        precipitation_dict["prcp"]=result.prcp
        precipitation.append(precipitation_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(precipitation)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations
    results=session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations=list(np.ravel(results))

    # Return a JSON list of stations from the dataset.
    return jsonify(stations)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperature observations (TOBS) for the previous year"""
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=one_year_ago).filter(Measurement.station=='USC00519281').all()

    session.close()

    # Convert the query results to a dictionary using `date` as the key and `tobs` as the value.
    tobs=[]
    for result in results:
        tobs_dict={}
        tobs_dict["date"]=result.date
        tobs_dict["tobs"]=result.tobs
        tobs.append(tobs_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(tobs)

# Start route
@app.route("/api/v1.0/temp/<start>")
def start_descriptives(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range."""

    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')

    #converting start date
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    tavg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= most_recent_date).scalar()
    tmin = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= most_recent_date).scalar()
    tmax = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= most_recent_date).scalar()

    session.close()

    descriptives = {"TMIN": tmin, "TMAX": tmax, "TAVG" : tavg}
    return jsonify(descriptives)

# Start-end route
@app.route("/api/v1.0/temp/<start>/<end>")
def start_end_descriptives(start, end):
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        most_recent_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    
        #Convert start date
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    
        tavg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).scalar()
        tmin = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).scalar()
        tmax = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).scalar()
    
        session.close()
    
        descriptives = {"TMIN": tmin, "TMAX": tmax, "TAVG" : tavg}
        return jsonify(descriptives)

if __name__ == "__main__":
    app.run(debug=True)