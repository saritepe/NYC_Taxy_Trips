# NYC_Taxy_Trips
NYC Taxy Trip Analysis For 2016

I build a solution that takes NYC Taxy trip data 2016 and finds popular routes and hexagons.
I extracted only March data to be able to fit at version control.

![PopulerRoute](Teknasyon%20Data%20Engineer%20Challange.png)


First of all, I did not have source to get data real time. So I build an application that takes data from parquet file
and send it to RabbitMQ row by row. This way I had a chance to process data real time, when I read from queue.
After that I eliminate data with date filter and wrong coordinates with filtering 0 lat and longs.  
After eliminating data, I set a sorted list at Redis. This way every time new data comes, it will add its hexagon and route score.
Then I build an API to get populer hexes and routes from Redis when it's needed.

To be able to run application, docker and docker-compose are needed.
To get data from API you will need to use curl or Postman or similar.

After cloning project you can run docker-compose up -d at location of project. 

You can watch Rabbitmq Queues with http://localhost:15672/ (user--guest pw--guest)
application logs with http://localhost:9000 (user--admin pw--admin)
Monitor redis with http://localhost:8001/


```
docker-compose up -d 
```

While application is working you can get populer routes by get method using curl. 
It will show 5 data if it does not specify at request.

Day Parts are
```
['Night', 'Morning', 'Noon', 'Evening']
```


For Routes
```
curl --location --request GET 'http://127.0.0.1:5001/routes'

curl --location --request GET 'http://127.0.0.1:5001/routes?day_part=Morning'

curl --location --request GET 'http://127.0.0.1:5001/routes?day_part=Morning&route_count=2'
```


For Hexes
```
curl --location --request GET 'http://127.0.0.1:5001/hexes?hex_type=pickup'
curl --location --request GET 'http://127.0.0.1:5001/hexes?hex_type=dropoff'
curl --location --request GET 'http://127.0.0.1:5001/hexes?hex_type=dropoff&day_part=Morning'
```

You can close all applications by
```
docker-compose down
```