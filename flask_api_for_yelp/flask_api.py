# Based on: https://gist.github.com/jamescalam/0b309d275999f9df26fa063602753f73

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
from hashlib import md5
from os.path import isfile
from collections import Counter
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
api = Api(app)
import requests
import time
import concurrent.futures                    
from preprocess import get_summary

class Topics(Resource):

    def post(self):

        # for testing
        # return {'data': 'stuff'}, 200   
        # return {"data": {"pasta": "The pasta sauce has weird taste. The pasta was okay if a bit salty. The pizza and the pasta were not upto standard.", "staff": "The staff was great pizza wasn't sitting out for too long. the staff was very kind and attentive to our needs and the options and names of their pizzas were so cute most of them named after The staff was very friendly too..", "restaurant": "Maybe it was an off night for this Pizza restaurant. Often times when you have special instructions on DoorDash the restaurants disregard it. Came here spontaneously with some coworker s for a meal and came by this restaurant by chance.", "sauce": "The melding of the spices flavors cheese and sauce along with the toppings really make this a first rate pizza. The pasta sauce has weird taste. The sauce shouldn't be a watered-down version of the actual curry.", "bombay": "Ordered Bombay Pizza and Indian Style Garlic Bread. This review is primarily for the Bombay and Bollywood pizzas. There are four separate kinds of pizzas to choose from warriors pizza (pepperoni) sharks pizza (meat lover's pizza) half moon bay and Bombay paneer tikka", "bread": "The layer of cheese doesn't melt on top of the \"bread\" and you can taste the two layers separately. Indian pizza tests like eating a curry with bread. but they way this garlic bread was made it tasted great.", "garlic bread": "The garlic bread was better tasting than the pizza itself. The garlic \"bread\" looked indistinguishable from a small pizza but was quite garlicky. Ended up ordering a large pizza and garlic bread online.", "food": "Really tasty and flavorful food clean restaurant and friendly service! Nice customer service and food was fantastic. All the food was good and will return for beer and pizza.", "topping": "The melding of the spices flavors cheese and sauce along with the toppings really make this a first rate pizza. The pizza was definitely a California style pizza with a thin crust and the toppings were very generous. Lots of toppings.", "flavor": "The melding of the spices flavors cheese and sauce along with the toppings really make this a first rate pizza. The flavor tastes like the dishes they represent really well. There was some white sauce which didn't have any particular flavor.", "price": "It was fun to try the food was pretty good the service was good and the prices were good. The menu items were really good and the prices are really affordable. BUT the size and price of these pizzas need work.", "service": "It was fun to try the food was pretty good the service was good and the prices were good. Service was friendly and the place looked clean.  Gur was kind and the quality of their service is noticeable.", "cheese": "The melding of the spices flavors cheese and sauce along with the toppings really make this a first rate pizza. The layer of cheese doesn't melt on top of the \"bread\" and you can taste the two layers separately. They tend to go light on the cheese.", "time": "Delivery was on time and they included cute The pizza crust was crunchy and chewy at the same time. If there was ever a time to support local/family-owned businesses it's now.", "pepperoni": "the toppings and pepperoni Kinda greasy from all that pepperoni but not in a bad way at all. There are four separate kinds of pizzas to choose from warriors pizza (pepperoni) sharks pizza (meat lover's pizza) half moon bay and Bombay paneer tikka", "lot": "lots of seating-plenty of tvs-very clean!Really good Indian pizza. It takes a lot of time There was a lot to choose from", "one": "Write home about this one? hit!I haven't tried their traditional pizzas but their Indian ones are to die for. Tried the paneer and the mushroom one!", "crust": "Crust was crispy. Another complaint was that the crust was too flimsy and pale on the bottom. more before putting the pizza on so the crust at the bottom crisps up more.", "place": "too!First time ordering delivery from this place. Where this place mainly falls short is the flavor. This place is it."}}, 200

        print('entered post', self)
        request.get_json(force=True)
        parser = reqparse.RequestParser()  # initialize parser
        parser.add_argument('url', required=True, type=str)  # add args
        parser.add_argument('numPages', required=True, type=int)
        print('at args')
        args = parser.parse_args()  # parse arguments to dictionary
        
        print('at yelp urls')
        yelp_urls = []

        for page_num in range(0, args['numPages']):
            yelp_urls.append(args['url'] + '?start=' + str(20 * page_num))

        def download_yelp_page(yelp_url):
            yelp_html = requests.get(yelp_url).text
            yelp_name = md5(yelp_url.encode()).hexdigest()
            yelp_name = f'{yelp_name}.html'

            if not isfile(yelp_name):
                print('downloading file')
                with open(yelp_name, 'w') as yelp_file:
                    yelp_file.write(yelp_html)
                    print(f'{yelp_name} was downloaded...')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(download_yelp_page, yelp_urls)

        print('at reviews')
        reviews = Counter()

        for yelp_url in yelp_urls:
            yelp_name = md5(yelp_url.encode()).hexdigest()
            yelp_name = f'{yelp_name}.html'

            with open(yelp_name) as f:
                html = f.read()

            soup = BeautifulSoup(html, "html.parser")
            for i, item in enumerate(soup.select("li p span")):
                reviews[item.get_text()] += 1

        customer_reviews = []
        for key, val in reviews.items():
            if val == 1:
                customer_reviews.append(key)
        customer_reviews = ''.join(customer_reviews)
        # print(customer_reviews)

        categories = []
        for item in soup.select('span span a'):
            if item.get('class') and item.get('href'):
                categories.append(item.get_text())
        ' '.join(categories)

        return {'data': get_summary(customer_reviews, categories)}, 200    


api.add_resource(Topics, '/topics')  # add endpoints

if __name__ == '__main__':
    app.run()  # run our Flask app




    