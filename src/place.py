import math

from parsers.website_parser import WebsiteParser as wp

class Place:
    def __init__(self, place):
        self.id = place.get("id")
        self.types = place.get("types", [])
        self.national_phone_number = place.get("nationalPhoneNumber")
        self.rating = place.get("rating")
        self.google_maps_uri = place.get("googleMapsUri")
        self.website_uri = place.get("websiteUri")
        self.business_status = place.get("businessStatus")
        self.user_rating_count = place.get("userRatingCount")
        self.display_name = place.get("displayName", {}).get("text")
        
        # Fix reviews: ensure it's always a list of dicts
        self.reviews = place.get("reviews", []) or []
        # Review summary text
        self.review_summary = (
            place.get("reviewSummary", {})
                 .get("text", {})
                 .get("text")
        )
        
        self.emails = self.find_email()
        self.lead_score = self.score_place()

    def __str__(self):
        return (
            f"{self.display_name}\n"
            f"  ID: {self.id}\n"
            f"  Types: {', '.join(self.types)}\n"
            f"  Phone: {self.national_phone_number or 'N/A'}\n"
            f"  Rating: {self.rating} ({self.user_rating_count} reviews)\n"
            f"  Status: {self.business_status}\n"
            f"  Website: {self.website_uri or 'N/A'}\n"
            f"  Google Maps: {self.google_maps_uri}\n"
            f"  Review Summary: {self.review_summary or 'N/A'}\n"
            f"  Emails: {self.emails}\n"
            f"  Lead Score: {self.lead_score} / 5.00\n"
            f"  Reviews: {len(self.reviews)} found"
        )
    
    def find_email(self):
        print(f'        Looking for {self.display_name} email')
        emails = wp.extract_emails(self.website_uri) if self.website_uri else [] 
        
        if emails:
            print(f'        Email found: {emails}')
        else:
            print(f'        No email found')
        return emails
    
    def score_place(self):
        raw_score = 0

        # Business status
        if self.business_status == "OPERATIONAL":
            raw_score += 3
        elif self.business_status == "CLOSED_PERMANENTLY":
            return 0.0

        # Friction Index (reviews x low rating)
        if self.rating and self.user_rating_count:
            friction = (5 - self.rating) * math.log(1 + self.user_rating_count, 10)
            raw_score += friction * 2  # weight it stronger than raw rating
        elif self.rating:
            raw_score += (5 - self.rating)

        # Online visibility
        if self.review_summary:
            raw_score += 2
        if self.google_maps_uri:
            raw_score += 1
        if self.website_uri:
            raw_score += 2

        # Emails
        if self.emails:
            raw_score += 2

        # Normalize to 5
        max_score = 20  # adjust if weights increase
        normalized = min(5, (raw_score / max_score) * 5)
        return round(normalized, 2)
