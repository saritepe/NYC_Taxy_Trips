import pika
import time
import json
import logging
import sys
import os
import traceback
from dotenv import load_dotenv
from src.nyc_trip import NycTrip
import redis
from pygelf import GelfTcpHandler

load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
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
def callback(ch, method, properties, body):
    try:
        logger.debug(f"Nyc Trip Data: {body.decode()} read from rabbitmq.")
        nyc_trip = NycTrip(body.decode())
        if nyc_trip.is_eligible:
            r.zincrby('pickup_hex_count', 1, nyc_trip.pickup_hex_count_key)
            r.zincrby('dropoff_hex_count', 1, nyc_trip.dropoff_hex_count_key)
            r.zincrby('route', 1, nyc_trip.route_key)
            r.zincrby(f'{nyc_trip.day_part}_route', 1, nyc_trip.route_key)
            r.zincrby(f'{nyc_trip.day_part}_pickup_hex_count', 1, nyc_trip.pickup_hex_count_key)
            r.zincrby(f'{nyc_trip.day_part}_dropoff_hex_count', 1, nyc_trip.dropoff_hex_count_key)
            logger.info(f"Nyc Trip Data is eligible and sent to redis.")
        else:
            logger.info(f"Nyc Trip Data: {nyc_trip.pickup_datetime}, {nyc_trip.pickup_hex_code}, {nyc_trip.dropoff_hex_code} is not eligible.")
    except:
        logger.error(f"Could not parse json data : {body.decode()}")
        traceback.print_exc()

    ch.basic_ack(delivery_tag=method.delivery_tag)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='nyc_trip_data', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='nyc_trip_data', on_message_callback=callback)

    channel.start_consuming()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
