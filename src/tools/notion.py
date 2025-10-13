import requests
from place import Place
from tools.keys import get_secret

class Notion:
    def __init__(self, api_key=None, database_id=None, data_source_id=None):
        self.api_key = api_key or get_secret("NOTION_API_KEY")
        self.database_id = database_id or get_secret("NOTION_DATABASE_ID")
        self.data_source_id = data_source_id or get_secret("NOTION_DATA_SOURCE_ID")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2025-09-03",
        }

    @staticmethod
    def chunk_text(text, max_length=1500):
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

    def fetch_reviewed_leads(self):
        """Fetch reviewed leads with Email property and Email Sample toggle content."""
        query_url = f"https://api.notion.com/v1/data_sources/{self.data_source_id}/query"
        payload = {
            "filter": {
                "property": "Lead Status",
                "status": {"equals": "Reviewed"}
            },
            "page_size": 100
        }

        reviewed_leads = []
        has_more = True
        next_cursor = None

        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor

            res = requests.post(query_url, headers=self.headers, json=payload)
            if res.status_code != 200:
                print(f"❌ Error fetching reviewed leads: {res.status_code} - {res.text}")
                break

            data = res.json()
            results = data.get("results", [])

            for page in results:
                try:
                    page_id = page["id"]

                    # Basic info
                    name_prop = page["properties"].get("Name", {}).get("title", [])
                    name = name_prop[0]["text"]["content"] if name_prop else "Unnamed"

                    google_place_id_prop = page["properties"].get("Google Place ID", {}).get("rich_text", [])
                    google_place_id = google_place_id_prop[0]["text"]["content"] if google_place_id_prop else None

                    email_prop = page["properties"].get("Email", {}).get("rich_text", [])
                    email = email_prop[0]["text"]["content"] if email_prop else None

                    # Fetch Email Sample toggle content
                    email_sample = self._fetch_email_sample_toggle(page_id)

                    reviewed_leads.append({
                        "id": page_id,
                        "name": name,
                        "google_place_id": google_place_id,
                        "email": email,
                        "email_sample": email_sample,
                    })

                except Exception as e:
                    print(f"⚠️ Error parsing reviewed lead: {e}")

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")

        print(f"📋 Retrieved {len(reviewed_leads)} reviewed leads with Email Samples.")
        return reviewed_leads


    def _fetch_email_sample_toggle(self, page_id):
        """Retrieve the content of the 'Email Sample' toggle block for a given page."""
        blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        all_blocks = []
        next_cursor = None
        has_more = True

        # Gather all child blocks
        while has_more:
            params = {"page_size": 100}
            if next_cursor:
                params["start_cursor"] = next_cursor

            res = requests.get(blocks_url, headers=self.headers, params=params)
            if res.status_code != 200:
                print(f"❌ Error fetching blocks for page {page_id}: {res.status_code} - {res.text}")
                return None

            data = res.json()
            all_blocks.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")

        # Find the "Email Sample" toggle
        for block in all_blocks:
            if block["type"] == "toggle":
                toggle_text = "".join([
                    rt["text"]["content"] for rt in block["toggle"].get("rich_text", [])
                ]).strip()
                if toggle_text.lower() == "email sample":
                    toggle_id = block["id"]
                    return self._extract_toggle_content(toggle_id)

        return {"email_subject": None, "email_body": None}


    def _extract_toggle_content(self, toggle_id):
        """Extract the subject and body text from the children of an 'Email Sample' toggle block."""
        toggle_url = f"https://api.notion.com/v1/blocks/{toggle_id}/children"
        res = requests.get(toggle_url, headers=self.headers)
        if res.status_code != 200:
            print(f"❌ Error fetching toggle children: {res.status_code} - {res.text}")
            return {"email_subject": None, "email_body": None}

        data = res.json()
        contents = []
        for child in data.get("results", []):
            if child["type"] == "paragraph":
                text_content = "".join([
                    t["text"]["content"] for t in child["paragraph"].get("rich_text", [])
                ])
                contents.append(text_content)

        # Combine paragraph text into a single string
        full_text = "\n".join(contents).strip()

        # Extract subject and body
        subject = None
        body = None

        if "Subject:" in full_text:
            parts = full_text.split("Subject:", 1)[1].strip().split("\n", 1)
            subject = parts[0].strip()
            body = parts[1].strip() if len(parts) > 1 else ""
        else:
            body = full_text

        return {
            "email_subject": subject,
            "email_body": body
        }
    
    def update_lead_status_to_sent(self, page_id: str):
        """Update the Lead Status of a given page to 'Sent'."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {
            "properties": {
                "Lead Status": {
                    "status": {"name": "Sent"}
                }
            }
        }

        res = requests.patch(url, headers=self.headers, json=payload)

        if res.status_code == 200:
            print(f"✅ Successfully updated Lead Status to 'Sent' for page {page_id}")
            return True
        else:
            print(f"❌ Failed to update Lead Status for {page_id}: {res.status_code} - {res.text}")
            return False
