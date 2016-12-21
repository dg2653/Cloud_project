from pymongo import MongoClient
from bson.son import SON
from bson.objectid import ObjectId


class MongoDbHandler:

    def __init__(self, connection_url, db_name):
        self.connection_url = connection_url
        self.db_name = db_name

    def make_connection(self):
        client = MongoClient(self.connection_url, connect=False)
        db = client[self.db_name]
        return db, client
    
    def get_aws_credentials(self):
        db, client = self.make_connection()
        obj = db.aws_credentials.find_one()
        result = [obj['access_token'], obj['access_token_secret']]
        client.close()
        return result
    
    def get_all_restaurants(self):
        db, client = self.make_connection()
        results = db.restaurants.find({"coordinates":{"$exists":True}},{"coordinates":1, "name":1, "_id":1})
        data = [{} for i in range(results.count())]
        for i in range(results.count()):
            data[i]["coordinates"] = results[i]["coordinates"]
            data[i]["name"] = results[i]["name"]
            data[i]["_id"] = str(results[i]["_id"])
        client.close()
        return data

    def get_restaurants(self, restaurant_name, city, categories):
        db, client = self.make_connection()
        query = {}
        if len(categories)>0:
            query['categories'] = {"$in":categories}
        if city!="":
            query['city'] = city
        if restaurant_name!="":
            query['name'] = restaurant_name
        results = db.restaurants.find(query,{"coordinates":1, "name":1, "_id":1}).limit(1000)
        data = list(results)
        client.close()
        return data


    def get_restaurant_info(self, restaurant_id, only_data = False):
        db, client = self.make_connection()
        results = db.restaurants.find({"_id": ObjectId(restaurant_id)})
        data = list(results)
        if only_data:
            client.close()
            return data[0]
        reviews = list(db.reviews.find({"business_id":data[0]['business_id']}))
        client.close()
        return data, reviews


    def get_distinct_cities(self):
        db, client = self.make_connection()
        results = sorted(db.restaurants.distinct("city"))
        client.close()
        return results

