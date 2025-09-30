from parsers.email_parser import EmailParser as ep

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
        self.display_name = place.get("displayName").get("text")
        self.review_summary = place.get("reviewSummary", {}).get("text", {}).get("text")
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
            f"  Lead Score: {self.lead_score} / 5.00"
        )
    
    def find_email(self):
        print(f'        Looking for {self.display_name} email')
        emails = ep.extract_emails(self.website_uri) if self.website_uri else [] # check for email if not empty list
        
        if len(emails) > 0:
            print(f'        Email founds: {emails}')
        else:
            print(f'        No email found')
        return emails
    
    def score_place(self):
        raw_score = 0

        # Contactability
        if self.national_phone_number:
            raw_score += 3
        if self.website_uri:
            raw_score += 2
        if len(self.emails) > 0:  # assumes self.emails is a list or None
            raw_score += 5  # emails are high-priority for outreach

        # Business status
        if self.business_status == "OPERATIONAL":
            raw_score += 3
        elif self.business_status == "CLOSED_PERMANENTLY":
            return 0.0  # treat closed as lowest score

        # Reputation
        if self.rating:
            raw_score += self.rating * 1.5
        if self.user_rating_count:
            if self.user_rating_count > 100:
                raw_score += 3
            elif self.user_rating_count > 20:
                raw_score += 2
            elif self.user_rating_count > 0:
                raw_score += 1

        # Online visibility
        if self.review_summary:
            raw_score += 2
        if self.google_maps_uri:
            raw_score += 1

        # Normalize (cap at 5 just in case)
        max_score = 26.5  # updated max to reflect extra email weight
        normalized = min(5, (raw_score / max_score) * 5)
        return round(normalized, 2)


