import requests
from dotenv import load_dotenv
import os
from typing import List

from place import Place

DEFAULT_FIELD_MASK = "places.id,places.displayName,places.googleMapsUri,places.types,places.websiteUri,places.nationalPhoneNumber,places.businessStatus,places.rating,places.userRatingCount,places.reviewSummary"

load_dotenv()
places_api_key = os.getenv("GOOGLE_API_KEY")
places_api_url = os.getenv("GOOGLE_API_URL")

class PlaceParser:
    def __init__(self, field_mask: str = DEFAULT_FIELD_MASK):
        self.field_mask = field_mask
        self.places = {}

    def search(self, search_query: str):
        '''
        Sends request to maps api, 
        if place not in places dict then add to list
        '''

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": places_api_key,
            "X-Goog-fieldMask": self.field_mask
        }

        body = {
            "textQuery": search_query
        }

        response = requests.post(places_api_url, headers=headers, json=body)

        if response.status_code == 200:
            data = response.json()
            results = data.get("places", [])
            for place in results:
                if place['id'] not in self.places:
                    self.places[place['id']] = Place(place)
        else:
            print("Error:", response.status_code, response.text)

    def mass_search(self, queries: List[str]):
        for q in queries:
            self.search(q)

if __name__ == '__main__':
    p = PlaceParser()
    p.mass_search(["Bookstores in Newark, NJ", "Restaurants in Philadelphia, PA"])

    for place in p.places.values():
        print(place)
