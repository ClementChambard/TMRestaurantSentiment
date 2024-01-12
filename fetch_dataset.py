import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
headers = {
    'Authorization': f'Bearer {api_key}',
}

def get_reviews(business_id):
    url = f'https://api.yelp.com/v3/businesses/{business_id}/reviews'
    response = requests.get(url, headers=headers)
    reviews = response.json()['reviews']
    return reviews

def get_businesses(offset=0, limit=50):
    url = 'https://api.yelp.com/v3/businesses/search'
    params = {
        'term': 'restaurants',
        'location': 'New York', # area with a lot of restaurants
        'limit': limit,
        'offset': offset,
    }
    response = requests.get(url, headers=headers, params=params)
    businesses = response.json()['businesses']
    return businesses

def create_dataset(name, desired_reviews_per_rating = 2000):

    data = {'text': [], 'rating': []}
    reviews_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    offset = 0
    while any(count < desired_reviews_per_rating for count in reviews_count.values()):
        businesses = get_businesses(offset)
        if len(businesses) == 0:
            print("out of businesses")
            break

        for business in businesses:
            reviews = get_reviews(business['id'])
        
            for review in reviews:
                rating = review['rating']
            
                # Check if we need more reviews for this rating
                if reviews_count[rating] < desired_reviews_per_rating:
                    data['text'].append(review['text'])
                    data['rating'].append(rating)
                    reviews_count[rating] += 1

                    # Check if we have reached the desired count for all ratings
                    if all(count >= desired_reviews_per_rating for count in reviews_count.values()):
                        break
            print(reviews_count)

        offset += len(business)

    df = pd.DataFrame(data)
    df.to_csv(name, index=False)

if __name__ == "__main__":
    create_dataset("restaurant_reviews.csv")
    print("done")