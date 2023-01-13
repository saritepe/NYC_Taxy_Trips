import pika
import sys
import os
from dotenv import load_dotenv
import pandas as pd
import logging
import traceback
from pygelf import GelfTcpHandler

load_dotenv()  # take environment variables from .env.

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
GELF_HOST = os.getenv('GELF_HOST')

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s:%(message)s',
                    handlers=[
                        logging.FileHandler('app.log', mode='w'),
                        logging.StreamHandler(sys.stdout),
                        GelfTcpHandler(host=GELF_HOST, port=12201)
                    ], level=logging.INFO)
logger = logging.getLogger(__name__)
def send_nyc_trip_data():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='nyc_trip_data', durable=True)

    nyc_trip_data = pd.read_parquet('nyc_green_trips_2016_03.parquet.gzip')

    #nyc_trip_data = nyc_trip_data.head(1000)
    nyc_trip_data = nyc_trip_data.sample(frac=0.25, replace=True, random_state=1)

    for idx, row in nyc_trip_data.iterrows():
        try:
            trip_record = str(row.to_json())
            logger.info(trip_record)
            channel.basic_publish(
                exchange='',
                routing_key='nyc_trip_data',
                body=trip_record,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ))
        except:
            logger.error("Row could not pushed to RabbitMQ.")
            traceback.print_exc()

    connection.close()

    logger.info(f"Row count : {len(nyc_trip_data)}")


if __name__ == '__main__':
    send_nyc_trip_data()