import requests
from dotenv import load_dotenv
import os

# set up
load_dotenv()
places_api_key = os.getenv("GOOGLE_API_KEY")
places_api_url = os.getenv("GOOGLE_API_URL")

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": places_api_key,
    "X-Goog-FieldMask": "places.id,places.displayName,places.googleMapsUri,places.types,places.websiteUri,places.nationalPhoneNumber,places.businessStatus,places.rating,places.userRatingCount,places.reviewSummary"
}

body = {
    "textQuery": "Bookstores in Newark, NJ"
}

response = requests.post(places_api_url, headers=headers, json=body)

if response.status_code == 200:
    data = response.json()
    place = data.get("places", [])[0]
    for k,v in place.items():
        print(k,v)
else:
    pass



