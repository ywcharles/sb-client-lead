import os
import requests
from dotenv import load_dotenv
from place import Place

load_dotenv()

class Notion:
    def __init__(self, api_key=None, database_id=None, data_source_id=None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        self.data_source_id = data_source_id or os.getenv("NOTION_DATA_SOURCE_ID")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        }

    @staticmethod
    def chunk_text(text, max_length=2000):
        if not text:
            return ["No content available."]
        return [text[i:i + max_length - 1] for i in range(0, len(text), max_length - 1)]

    def make_toggle_block(self, title: str, content: str):
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}],
                },
            }
            for chunk in self.chunk_text(content)
        ]
        return {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": title}}],
                "children": children,
            },
        }

    def export_place(self, place: Place):
        url = "https://api.notion.com/v1/pages"
        reviews_text = "\n__________\n".join([review["text"]["text"] for review in place.reviews])

        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": place.display_name or "Unknown"}}]},
                "Business Status": {"rich_text": [{"text": {"content": place.business_status or ""}}]},
                "Lead Status": {"status": {"name": "Not Reviewed"}},
                "Email": {"rich_text": [{"text": {"content": ", ".join(place.emails or [])}}]},
                "Phone Number": {"rich_text": [{"text": {"content": place.national_phone_number or ""}}]},
                "website": {"url": place.website_uri or None},
                "Business Type": {"rich_text": [{"text": {"content": ", ".join(place.types or [])}}]},
                "Lead Score": {"number": place.lead_score or 0},
                "Google Maps Rating Score": {"number": place.rating or 0},
                "Google Maps Rating Count": {"number": place.user_rating_count or 0},
                "Google Maps Link": {"url": place.google_maps_uri or None},
                "Google Place ID": {"rich_text": [{"text": {"content": place.id or ""}}]},
            },
            "children": [
                self.make_toggle_block("Reviews", reviews_text),
                self.make_toggle_block("Reviews Summary", place.review_summary),
                self.make_toggle_block("UI Report", place.ui_report),
                self.make_toggle_block("Brief", place.brief),
                self.make_toggle_block("Pain Point Report", place.pain_point_report),
                self.make_toggle_block("Email Sample", place.email_sample),
            ],
        }

        res = requests.post(url, headers=self.headers, json=data)
        if res.status_code == 200:
            print(f"✅ Created Notion page for {place.display_name}")
        else:
            print(f"❌ Error: {res.status_code} - {res.text}")

    def fetch_all_place_ids(self):
        url = f"https://api.notion.com/v1/data_sources/{self.data_source_id}/query"
        place_ids = set()
        payload = {"page_size": 100}
        has_more = True
        next_cursor = None

        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor

            res = requests.post(url=url, headers=self.headers, json=payload)
            if res.status_code != 200:
                print(f"❌ Error fetching place IDs: {res.status_code} - {res.text}")
                break

            data = res.json()
            results = data.get("results", [])
            for page in results:
                try:
                    # Extract the Google Place ID property safely
                    prop = page["properties"].get("Google Place ID", {})
                    text_list = prop.get("rich_text", [])
                    if text_list:
                        place_id = text_list[0]["text"]["content"].strip()
                        if place_id:
                            place_ids.add(place_id)
                except Exception as e:
                    print(f"⚠️ Error parsing place ID: {e}")

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")

        print(f"📦 Retrieved {len(place_ids)} existing place IDs from Notion data source.")
        return place_ids
