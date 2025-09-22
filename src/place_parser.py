import requests
from dotenv import load_dotenv
from openpyxl import Workbook

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
        """
        Sends request to maps api,
        if place not in places dict then add to list
        """

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": places_api_key,
            "X-Goog-fieldMask": self.field_mask,
        }

        body = {"textQuery": search_query}

        response = requests.post(places_api_url, headers=headers, json=body)

        if response.status_code == 200:
            data = response.json()
            results = data.get("places", [])
            for place in results:
                if place["id"] not in self.places:
                    self.places[place["id"]] = Place(place)
        else:
            print("Error:", response.status_code, response.text)

    def mass_search(self, queries: List[str]):
        for q in queries:
            self.search(q)

    def export_excel(self, filename: str = "places.xlsx"):
        wb = Workbook()
        ws = wb.active
        ws.title = "Places"

        # Define headers
        headers = [
            "id",
            "display_name",
            "types",
            "phone",
            "rating",
            "user_rating_count",
            "status",
            "website",
            "google_maps_uri",
            "review_summary",
            "lead_score",
        ]
        ws.append(headers)

        # Write data rows
        for place in self.places.values():
            ws.append(
                [
                    place.id,
                    place.display_name,
                    ", ".join(place.types),
                    place.national_phone_number or "",
                    place.rating or "",
                    place.user_rating_count or "",
                    place.business_status or "",
                    place.website_uri or "",
                    place.google_maps_uri or "",
                    place.review_summary or "",
                    place.lead_score,
                ]
            )

        # Save to file
        wb.save(filename)


if __name__ == "__main__":
    sample_queries = [
        "small business Bergen County NJ",
        "local business Bergen County NJ",
        "shop Bergen County NJ",
        "store Bergen County NJ",
        "retail Bergen County NJ",
        "boutique Bergen County NJ",
        "artisan Bergen County NJ",
        "handmade Bergen County NJ",
        "crafts Bergen County NJ",
        "gift shop Bergen County NJ",
        "bakery Bergen County NJ",
        "cafe Bergen County NJ",
        "restaurant Bergen County NJ",
        "florist Bergen County NJ",
        "jewelry Bergen County NJ",
        "home decor Bergen County NJ",
        "toy store Bergen County NJ",
        "stationery Bergen County NJ",
        "beauty salon Bergen County NJ",
        "barber shop Bergen County NJ",
        "fitness studio Bergen County NJ",
        "gallery Bergen County NJ",
        "thrift store Bergen County NJ",
        "clothing store Bergen County NJ",
        "market Bergen County NJ",
    ]
    p = PlaceParser()
    p.mass_search(sample_queries)
    p.export_excel()
