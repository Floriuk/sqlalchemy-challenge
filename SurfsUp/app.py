# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end_date><br/>"
    )

@app.route("/api/v1.0/precipitation")
def analysis():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Precipitation Analysis"""
    # Query
    latest_date = session.query(func.date(func.date('2017-08-23', '-1 year'))).scalar()
    session.query(measurement.date, measurement.prcp).filter(measurement.date >= latest_date).all()
    query_result = (
    session
    .query(measurement.date, measurement.prcp)
    .filter(func.date(measurement.date) >= latest_date)
    .order_by(measurement.date.asc())
    .all()
    )

    session.close()


    return  jsonify(dict(query_result))

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    "# of Stations"
    total_stations = session.query((station.station)).all()
    total_stations = list(np.ravel(total_stations))
    session.close()
    return jsonify(total_stations=total_stations)

@app.route("/api/v1.0/tobs")
def activestation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    "Active Station"
    station_counts = session.query(station.station, func.count(measurement.station)).\
    join(measurement, station.station == measurement.station).\
    group_by(station.station).\
    order_by(desc(func.count(measurement.station))).\
    all()

    most_active_station = station_counts[0][0]
    latest_date = session.query(func.date(func.date('2017-08-23', '-1 year'))).scalar()
    temperature_data = (
        session.query(measurement.date, measurement.tobs)
        .filter(measurement.station == most_active_station)
        .filter(measurement.date >= latest_date)
        .all()
    )
    session.close()
    return  jsonify(dict(temperature_data))

@app.route("/api/v1.0/<start>")
def startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    "Start date"

    temperature_data = (
        session.query(func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs))
        .filter(measurement.date >= start)
        .all()
    )
    temperature_data = list(np.ravel(temperature_data))
    session.close()
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end_date>")
def end_date(start, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    "Start date"

    temperature_data = (
        session.query(func.min(measurement.tobs),
        func.avg(measurement.tobs),
        func.max(measurement.tobs))
        .filter(measurement.date >= start, measurement.date<end_date)
        .all()
    )
    temperature_data = list(np.ravel(temperature_data))
    session.close()
    return jsonify(temperature_data)

if __name__ == '__main__':
    app.run(debug=True)