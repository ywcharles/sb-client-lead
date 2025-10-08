import random
import time
import requests
from openpyxl import Workbook

from typing import List

from agents.leads_agent import LeadsAgent
from place import Place
from tools.keys import get_secret
from tools.notion import Notion

DEFAULT_FIELD_MASK = "places.id,places.displayName,places.googleMapsUri,places.types,places.websiteUri,places.nationalPhoneNumber,places.businessStatus,places.rating,places.userRatingCount,places.reviewSummary,places.reviews"

places_api_key = get_secret("GOOGLE_API_KEY")
places_api_url = "https://places.googleapis.com/v1/places:searchText"


class PlaceParser:
    def __init__(self, field_mask: str = DEFAULT_FIELD_MASK):
        self.notion = Notion()
        self.field_mask = field_mask
        self.places = {}
        self.agent = LeadsAgent()
        self.visited = self.notion.fetch_all_place_ids()

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
                if place["id"] not in self.places and place["id"] not in self.visited:
                    print(f'    FOUND: {place["id"]}')
                    p = Place(place=place, leads_agent=self.agent)
                    if len(p.emails) > 0: # eliminate places with no emails
                        self.places[place["id"]] = p
        else:
            print("Error:", response.status_code, response.text)

    def mass_search(self, queries: List[str]):
        for q in queries:
            print(f'__Searching for {q}__')
            self.search(q)
            print(f'__Done searching for {q}__')

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
            "reviews",
            "emails",
            "lead_score",
            "ui_report",
            "brief",
            "pain_point_report",
            "email_sample"
        ]
        ws.append(headers)

        # Write data rows
       # Write data rows
        for place in self.places.values():
            # Extract review texts only (limit to 3 to avoid Excel bloat)
            review_texts = [r.get("text", {}).get("text", "") for r in place.reviews[:3]]
            
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
                    " | ".join(review_texts),   # new: compact review export
                    ", ".join(place.emails),
                    place.lead_score,
                    place.ui_report,
                    place.brief,
                    place.pain_point_report,
                    place.email_sample,
                ]
            )
        # Save to file
        wb.save(filename)

    def update_notion_with_places(self):
        for place in self.places.values():
            self.notion.export_place(place = place)
            time.sleep(random.uniform(0.4, 0.6)) 


if __name__ == "__main__":
    pass
