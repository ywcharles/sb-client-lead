from agents.leads_agent import LeadsAgent
from parsers.place_parser import PlaceParser
from parsers.website_parser import WebsiteParser as wp

import os
import re
import pickle

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
p.search("small business Bergen County NJ")
p.export_excel()

# os.makedirs("./places", exist_ok=True)

# def sanitize_filename(name: str) -> str:
#     """Replace illegal filename chars with underscores"""
#     return re.sub(r'[^a-zA-Z0-9_-]', "_", name)

# # for place in places:
# #     safe_name = sanitize_filename(place.display_name)
# #     file_path = f"./places/{safe_name}.pkl"
# #     with open(file_path, "wb") as f:
# #         pickle.dump(place, f)
# #     print(f"✅ Saved {place.display_name} -> {file_path}")

# with open("./places/The_Gift_Shoppe_at_Curbside_Confections.pkl", 'rb') as file:
#     place = pickle.load(file)

# # with open("./places/Love___Box.pkl", 'rb') as file:
# #     place = pickle.load(file)

# agent = LeadsAgent()
# ui_report = agent.generate_ui_report(place.website_uri)
# print(ui_report)
# brief = agent.generate_business_brief(place.website_uri)
# print(brief)
# pain = agent.generate_pain_points(brief=brief, ui_report=ui_report, reviews=place.reviews)
# print(pain)
# email = agent.generate_personalized_email(business_name=place.display_name, brief=brief, pain_point_report=pain)
# print(email)
# # report = agent.generate_ui_report(place.website_uri)
# # print(report)

# # brief = agent.generate_business_brief(place.website_uri)
# # print(brief)