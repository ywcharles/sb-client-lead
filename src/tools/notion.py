import os
import requests
from dotenv import load_dotenv

from place import Place

load_dotenv()

API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
MAX_BLOCK_TEXT = 2000

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03",
}


def chunk_text(text, max_length=MAX_BLOCK_TEXT):
    """Split long text into chunks compatible with Notion API limits."""
    if not text:
        return ["No content available."]
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def make_toggle_block(title: str, content: str):
    """Create a toggle block with one or more paragraph children."""
    children = []
    for chunk in chunk_text(content):
        children.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}],
                },
            }
        )
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title}}],
            "children": children,
        },
    }


def export_place_to_notion(place: Place):
    url = "https://api.notion.com/v1/pages"

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": place.display_name or "Unknown"}}]},
            "Business Status": {
                "rich_text": [{"text": {"content": place.business_status or ""}}]
            },
            "Lead Status": {"status": {"name": "Not Reviewed"}},
            "Email": {
                "rich_text": [{"text": {"content": ", ".join(place.emails or [])}}]
            },
            "Phone Number": {
                "rich_text": [
                    {"text": {"content": place.national_phone_number or ""}},
                ]
            },
            "website": {"url": place.website_uri or None},
            "Business Type": {
                "rich_text": [{"text": {"content": ", ".join(place.types or [])}}]
            },
            "Lead Score": {"number": place.lead_score or 0},
            "Google Maps Rating Score": {"number": place.rating or 0},
            "Google Maps Rating Count": {"number": place.user_rating_count or 0},
            "Google Maps Link": {"url": place.google_maps_uri or None},
            "Google Place ID": {"rich_text": [{"text": {"content": place.id or ""}}]},
        },
        "children": [
            make_toggle_block("Reviews", "\n__________\n".join([review['text']['text'] for review in place.reviews])),
            make_toggle_block("Reviews Summary", place.review_summary),
            make_toggle_block("UI Report", place.ui_report),
            make_toggle_block("Brief", place.brief),
            make_toggle_block("Pain Point Report", place.pain_point_report),
            make_toggle_block("Email Sample", place.email_sample),
        ],
    }

    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        print(f"✅ Created Notion page for {place.display_name}")
    else:
        print(f"❌ Error: {res.status_code} - {res.text}")
