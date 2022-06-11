import time
import os
import redis
from flask import Flask, render_template
import logging ,sys ,json_logging
from prometheus_flask_exporter import PrometheusMetrics

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

app = Flask(__name__)

metrics = PrometheusMetrics( app )

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

cache = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), password=REDIS_PASSWORD)
metrics.info( 'app_info' , 'Application info', version='1.0.3')



def get_hit_count():
    retries = 5
    while True:
        try:
            logger.info('iniciando contador' ) 
            hitss = cache.incr('hits')
            return hitss
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                logger.error( "Error de conexion" )
                logger.exception(exc)
                raise exc
            retries -=1
            time.sleep(0.5)

@app.route('/')
def hello():

    count = get_hit_count()
    message = "Hello Keepcoding!!!! I have been seen {} time HTML. \n".format(count)
    return  render_template("index.html",message=message)

@app.route('/health/liveness')   
def healthx():
    return "<h1><center>Liveness check completed</center><h1>"  

@app.route('/health/readiness')
def healthz():
    return "<h1><center>Readiness check completed</center><h1>"          


