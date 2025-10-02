from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from parsers.website_parser import WebsiteParser as wp

import os

from place import Place

load_dotenv()

OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")


class LeadsAgent:
    def __init__(self):
        self.base_model = ChatOpenAI(model="gpt-4o", api_key=OPEN_AI_API_KEY)

    def generate_pain_points(self, place: Place):
        prompt = f"""
You are a consultancy company looking for new clients. 
You offer StudentBrains offers = automation (ops, sales, support), website redesign, consulting (org/process), bookkeeping/accounting.

Given the business below
Business: {place.display_name}
Types: {', '.join(place.types)}
Google Maps Reviews Summary: {place.review_summary}
Website content: {wp.extract_html_contents(place.website_uri)}

Identify painpoints or area of improvement within the business that could benefit from your services.
Only output issues you can identify with confidence. Do not make assumptions
"""
        resp = self.base_model.invoke(prompt)
        return resp.content.strip()