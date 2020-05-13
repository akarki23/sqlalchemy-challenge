# Dependencies & Setup
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Setup Flask
app = Flask(__name__)

# `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    
    return session.\
        query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        all()

# Flask Routes

# Home Page
@app.route("/")
def main():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]<br/>"
        f"/api/v1.0/[start]/[end]"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query final date
    final_date_query = session.\
        query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).\
        all()
    # Set max date and begin date
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(366)
    # Query precipitation data
    precipitation_data = session.\
        query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).\
        all()
    # Create a {} to store the precipitation data
    results_dict = {}
    # Loop through query and store in {}
    for result in precipitation_data:
        results_dict[result[0]] = result[1]
    # Close session
    session.close()
    # Return json object
    return jsonify(results_dict)

# Stations
@app.route("/api/v1.0/stations")
def stations():
    # Query stations data
    stations = session.\
        query(Station).\
        all()
    # Create a [] to store stations data
    stations_list = []
    # Loop through query store data in []
    for station in stations:
        station_dict = {}
        station_dict["ID"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)
    # Close session
    session.close()
    # Return json object
    return jsonify(stations_list)

# TOBs
@app.route("/api/v1.0/tobs")
def tobs():
    # Query final date
    final_date_query = session.\
        query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).\
        all()
    # Set max date and begin date
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(366)
    # Query TOBs data
    results = session.\
        query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).\
        all()
    # Create a [] to store TOBs data
    tobs_list = []
    # Loop through query and store in a {}, then store that into a []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)
    # Close session
    session.close()
    # Return json object
    return jsonify(tobs_list)

# Start
@app.route("/api/v1.0/<start>")
def start(start):
    # Query final date
    final_date_query = session.\
        query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).\
        all()
    # Set max date
    max_date = final_date_query[0][0]
    # `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    temps = calc_temps(start, max_date)
    # Create a [] to store minimum, average, and maximum temperatures
    return_list = []
    # Create a {} to hold the start and end dates
    date_dict = {'start_date': start, 'end_date': max_date}
    # Append []
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})
    # Close session
    session.close()
    # Return json object
    return jsonify(return_list)

# Start_End
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    temps = calc_temps(start, end)
    # Create a [] to store minimum, average, and maximum temperatures
    return_list = []
    # Create a {} to hold the start and end dates
    date_dict = {'start_date': start, 'end_date': end}
    # Append []
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})
    # Close session
    session.close()
    # Return json object
    return jsonify(return_list)

# Run
if __name__ == "__main__":
    app.run(debug = True)
