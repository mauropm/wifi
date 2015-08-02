import time

from flask import Blueprint, request, jsonify
from webargs import Arg
from webargs.flaskparser import use_args
from sqlalchemy.sql import func



from app import app, db, debug, error
from app.models import Stream

mod_web_api = Blueprint('web_api', __name__, url_prefix='/api')


@mod_web_api.route('/')
def api_index():
    return "api root"


def round_arrival(minutes, value):
    return int(float(value) / (minutes * 60.0)) * (minutes * 60)


ping_args = {
    'min':Arg(float, required=False, default=float(time.time() - 3600)),
    'max':Arg(float, required=False, default=float(time.time())),
    'mac':Arg(str, required=False, default=None),
    'unique':Arg(bool, required=False, default=False)
}


@mod_web_api.route('/pings')
@use_args(ping_args)
def ping(args):
    data = []
    if args["unique"]:
        resultset = db.session.query(
            Stream.mac, Stream.manuf,
            func.min(Stream.arrival).label('min_arrival'),
            func.max(Stream.arrival).label('max_arrival'),
            func.avg(Stream.signal).label('avg_signal'))\
            .filter(Stream.arrival >= args["min"])\
            .filter(Stream.arrival <= args["max"])\
            .filter(Stream.signal != None)\
            .group_by(Stream.mac, Stream.manuf).all()
        for row in resultset:
            data.append({
                "mac":row.mac,
                "manuf":row.manuf,
                "avg_signal":int(row.avg_signal),
                "min_arrival":round_arrival(5, row.min_arrival),
                "max_arrival":round_arrival(5, row.max_arrival)
            })
    else:
        resultset = Stream.query\
            .filter(Stream.mac == args["mac"])\
            .filter(Stream.arrival >= args["min"])\
            .filter(Stream.arrival <= args["max"])\
            .order_by(Stream.arrival)
        for row in resultset:
            data.append({
                "mac":row.mac,
                "manuf":row.manuf,
                "arrival":str(row.arrival),
                "signal":row.signal
            })
    return jsonify(data=data)


