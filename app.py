import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)
    
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart_date&gt"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
        f"date_code = YYYY-MM-DD"
        f"date must in 2010-01-01 to 2017-08-23" 
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_dict = {}
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    for result in results:
        date_dict[result[0]] = result[1]

    return jsonify(date_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name)
    stations = []
    for station in results:
        unit = {}
        unit["name"] = station[1]
        unit["station id"] = station[0]
        stations.append(unit)
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    subquery = session.query(Measurement.station, func.count(Measurement.date))\
    .group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).first()
    station = subquery[0]
    
    results = session.query(Station.name, Measurement.station, Measurement.tobs, Measurement.date).filter(Measurement.date > '2016-12-31')\
    .filter(Measurement.station == station).filter(Station.station == station).order_by(Measurement.date)

    temps = []
    for result in results:
        t_dict = {}
        t_dict["name"]= result[0]
        t_dict["station id"]=result[1]
        t_dict["temperature"]=result[2]
        t_dict["date"]=result[3]
        temps.append(t_dict)
        
    session.close()
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def tobs_by_start(start):
    session = Session(engine)
    subquery = session.query(Measurement.date, func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(Measurement.date >= start).group_by(Measurement.date)
    return_list = []
    for elem in subquery:
        data = {}
        data["date"] = elem[0]
        data["temperatures"] = {"mean": elem[1], "max": elem[2], "min": elem[3]}
        return_list.append(data)
    session.close()
    return jsonify(return_list)
    
@app.route("/api/v1.0/<start>/<end>")
def tobs_by_bounds(start, end):
    session = Session(engine)
    query = session.query(Measurement.date, func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date)
    return_list = []
    for elem in query:
        data = {}
        data["date"] = elem[0]
        data["temperatures"] = {"mean": elem[1], "max": elem[2], "min": elem[3]}
        return_list.append(data)
    session.close()
    return jsonify(return_list)
    
    
    
if __name__ == '__main__':
    app.run(debug=True)