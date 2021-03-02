# flask_api

## Purpose is to provide a REST API that will give summary for a particular yelp business


## Run
```python flask_api.py```

## GET request
<!-- curl -X GET http://127.0.0.1:5000 -->

## POST request
<!-- curl -X POST -d '{"userId": "a3c", "name": "Holly", "city": "Paris"}' http://127.0.0.1:5000/users --header "Content-Type:application/json" -->
```curl -d "url=https://www.yelp.com/biz/bay-area-pizza-santa-clara&numPages=9" http://127.0.0.1:5000/topics```