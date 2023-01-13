import json
import h3
import pendulum


class NycTrip:
    def __init__(self, nyc_trip_json_str):
        self.nyc_trip_json_str = nyc_trip_json_str
        self.nyc_trip_json = json.loads(self.nyc_trip_json_str)
        self.pickup_timestamp = float(self.nyc_trip_json.get('lpep_pickup_datetime'))/ 1000
        self.dropoff_timestamp = float(self.nyc_trip_json.get('Lpep_dropoff_datetime')) / 1000
        self.pickup_datetime = self.convert_pickup_datetime_string_to_datetime()
        self.pickup_latitude = self.nyc_trip_json.get('Pickup_latitude')
        self.pickup_longitude = self.nyc_trip_json.get('Pickup_longitude')
        self.dropoff_latitude = self.nyc_trip_json.get('Dropoff_latitude')
        self.dropoff_longitude = self.nyc_trip_json.get('Dropoff_longitude')
        self.trip_distance = self.nyc_trip_json.get('Trip_distance')
        self.total_amount = self.nyc_trip_json.get('Total_amount')
        self.passanger_count = self.nyc_trip_json.get('Passenger_count')
        self.pickup_hex_code = h3.geo_to_h3(self.pickup_latitude, self.pickup_longitude, 7)
        self.dropoff_hex_code = h3.geo_to_h3(self.pickup_latitude, self.pickup_longitude, 7)
        self.day_part = self.calculate_day_part()
        self.is_eligible = self.check_date() and self.check_coordinates()
        self.route_key_with_day_part = f"day_part:{self.day_part}:pickup_hex:{self.pickup_hex_code}:dropoff_hex:{self.dropoff_hex_code}:route_count"
        self.pickup_hex_count_key_day_part = f"day_part:{self.day_part}:pickup_hex:{self.pickup_hex_code}:pickup_hex_count"
        self.dropoff_hex_count_key_day_part = f"day_part:{self.day_part}:dropoff_hex:{self.dropoff_hex_code}:dropoff_hex_count"

        self.route_key = f"pickup_hex:{self.pickup_hex_code}:dropoff_hex:{self.dropoff_hex_code}:route_count"
        self.pickup_hex_count_key = f"pickup_hex:{self.pickup_hex_code}:pickup_hex_count"
        self.dropoff_hex_count_key = f"dropoff_hex:{self.dropoff_hex_code}:dropoff_hex_count"

    def convert_pickup_datetime_string_to_datetime(self):
        pickup_datetime = pendulum.from_timestamp(self.pickup_timestamp)
        return pickup_datetime

    def calculate_day_part(self):
        pickup_hour = self.pickup_datetime.hour
        if 0 <= pickup_hour < 6:
            day_part = 'Night'
        elif 6 <= pickup_hour < 12:
            day_part = 'Morning'
        elif 12 <= pickup_hour < 18:
            day_part = 'Noon'
        else:
            day_part = 'Evening'

        return day_part

    def check_coordinates(self):
        if self.pickup_latitude != 0 and self.pickup_longitude != 0\
                and self.dropoff_latitude != 0 and self.dropoff_longitude != 0:
            return True
        else:
            return False

    def check_date(self):
        if self.pickup_datetime.year == 2016 and self.pickup_datetime.month == 3\
                and self.pickup_datetime.week_of_month == 1:
            return True
        else:
            return False




