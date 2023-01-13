import logging
import sys
import os
from dotenv import load_dotenv
import redis
from flask import Flask, request
import pandas as pd
from pygelf import GelfTcpHandler
import logging


app = Flask(__name__)

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
GELF_HOST = os.getenv('GELF_HOST')

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                    handlers=[
                        logging.FileHandler('app.log', mode='w'),
                        logging.StreamHandler(sys.stdout),
                        GelfTcpHandler(host=GELF_HOST, port=12201)
                    ], level=logging.INFO)

logger = logging.getLogger(__name__)
#logger.addHandler(GelfTcpHandler(host=GELF_HOST, port=12201))
logger.info('hello gelf')


def calculate_populer_routes(day_part='all', n=5):
    if day_part is None:
        day_part = 'all'
    if n is None:
        n = 5

    if day_part == 'all':
        redis_key = f"route"
    elif day_part in ['Night', 'Morning', 'Noon', 'Evening']:
        redis_key = f"{day_part}_route"
    else:
        redis_key = None

    routes = []
    print(redis_key)
    for route_key in r.zrange(redis_key, 0, n, desc=True, withscores=True):
        route_dict = dict()
        route_key_list = route_key[0].decode().split(':')
        route_dict['pickup_hex'] = route_key_list[1]
        route_dict['dropoff_hex'] = route_key_list[3]
        route_dict['count'] = route_key[1]
        routes.append(route_dict)

    return routes


def calculate_populer_hexes(hex_type, day_part='all', n=5):

    if hex_type not in ['pickup', 'dropoff']:
        return None

    if day_part is None:
        day_part = 'all'
    if n is None:
        n = 5

    if day_part == 'all':
        redis_key = f"{hex_type}_hex_count"
    elif day_part in ['Night', 'Morning', 'Noon', 'Evening']:
        redis_key = f"{day_part}_{hex_type}_hex_count"
    else:
        redis_key = None

    hexes = []
    print(redis_key)
    for hex_key in r.zrange(redis_key, 0, n, desc=True, withscores=True):
        tmp_dict = dict()
        pickup_hex = hex_key[0].decode().split(':')
        tmp_dict[hex_type] = pickup_hex[1]
        tmp_dict['count'] = hex_key[1]
        hexes.append(tmp_dict)

    return hexes

@app.route('/routes', methods=['GET'])
def find_routes():
    args = request.args
    day_part = args.get('day_part')
    route_count = args.get('route_count')

    if route_count is not None:
        route_count = int(route_count)
    result = calculate_populer_routes(day_part, route_count)
    print(result)
    return {'data': result}, 200  # return data and 200 OK code


@app.route('/hexes', methods=['GET'])
def find_hexes():
    args = request.args
    hex_type = args.get('hex_type')
    day_part = args.get('day_part')
    hex_count = args.get('hex_count')

    if hex_count is not None:
        hex_count = int(hex_count)
    result = calculate_populer_hexes(hex_type, day_part, hex_count)
    print(result)
    if result is not None:
        return {'data': result}, 200  # return data and 200 OK code
    else:
        return 'Error', 404

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
