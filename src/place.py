import math

from agents.leads_agent import LeadsAgent
from parsers.website_parser import WebsiteParser as wp
from tools.email import score_email
from tools.reviews import score_review_text, score_reviews_list

class Place:
    # Configurable thresholds
    MIN_SCORE_FOR_AI_REPORTS = 2.5  # Only generate AI reports if final score >= 2.5
    MIN_RATING_FOR_REPORTS = 3.5    # Skip if rating is too high (less pain points)
    MAX_RATING_FOR_REPORTS = 4.3    # Skip if rating is excellent (harder to pitch)
    MIN_REVIEW_COUNT = 5            # Need enough reviews to identify patterns
    
    def __init__(self, place, leads_agent=None, enable_thresholds=True):
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
        
        # Step 1: Find emails first
        self.emails = self.find_email()
        
        # Step 2: Calculate base score
        self.lead_score = self.score_place()
        print(f'        📊 Base score: {self.lead_score}/5.00')
        
        # Step 3: Update score with email and review quality
        if self.emails:
            self.update_score_with_email_and_reviews()
            print(f'        📊 Updated score: {self.lead_score}/5.00')
        
        # Initialize AI report fields
        self.ui_report = None
        self.brief = None
        self.pain_point_report = None
        self.email_sample = None
        self.email_subject = None  # NEW: Add email subject field
        self.skip_reason = None
        
        # Step 4: Generate AI reports based on FINAL score and thresholds
        if leads_agent and self.website_uri and self.emails:
            if enable_thresholds:
                if self._should_generate_reports():
                    self.generate_reports(leads_agent)
                else:
                    print(f'        ⭐️  Skipping AI reports for {self.display_name}: {self.skip_reason}')
            else:
                # Always generate if thresholds disabled
                self.generate_reports(leads_agent)

    def _should_generate_reports(self) -> bool:
        """
        Determine if this lead qualifies for expensive AI report generation.
        Returns True if reports should be generated, False otherwise.
        Sets self.skip_reason for logging.
        
        NOTE: This uses the UPDATED lead_score (after email/review scoring)
        """
        # Final lead score threshold (after email/review updates)
        if self.lead_score < self.MIN_SCORE_FOR_AI_REPORTS:
            self.skip_reason = f"Low lead score ({self.lead_score} < {self.MIN_SCORE_FOR_AI_REPORTS})"
            return False

        return True

    def generate_reports(self, leads_agent):
        """Generate all AI-powered reports for this place"""
        print(f'        🤖 Generating reports for {self.display_name}...')
        
        try:
            # Generate UI report
            print(f'          - UI Report')
            self.ui_report = leads_agent.generate_ui_report(self.website_uri)
            
            # Generate business brief
            print(f'          - Business Brief')
            self.brief = leads_agent.generate_business_brief(self.website_uri)
            
            # Generate pain point report (uses reviews)
            print(f'          - Pain Point Report')
            self.pain_point_report = leads_agent.generate_pain_points(
                self.brief, 
                self.ui_report, 
                self.reviews[:5]  # Limit to 5 reviews
            )
            
            # Generate email subject (NEW)
            print(f'          - Email Subject')
            self.email_subject = leads_agent.generate_email_subject(
                self.display_name,
                self.brief
            )
            
            # Generate personalized email
            print(f'          - Email Sample')
            self.email_sample = leads_agent.generate_personalized_email(
                self.emails[0],
                self.display_name,
                self.brief,
                self.pain_point_report
            )
            
            print(f'        ✅ Reports generated successfully')
        except Exception as e:
            print(f'        ❌ Error generating reports: {e}')

    def __str__(self):
        base_info = (
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
            f"  Reviews: {len(self.reviews)} found\n"
        )
        
        if self.ui_report:
            base_info += f"\n  UI Report Generated: Yes"
        if self.brief:
            base_info += f"\n  Brief Generated: Yes"
        if self.pain_point_report:
            base_info += f"\n  Pain Point Report Generated: Yes"
        if self.email_subject:
            base_info += f"\n  Email Subject Generated: Yes"
        if self.email_sample:
            base_info += f"\n  Email Sample Generated: Yes"
        if self.skip_reason:
            base_info += f"\n  AI Reports Skipped: {self.skip_reason}"
            
        return base_info
    
    def find_email(self):
        print(f'        🔍 Looking for {self.display_name} email')
        emails = wp.extract_emails(self.website_uri) if self.website_uri else [] 
        
        if emails:
            print(f'        ✉️  Email found: {emails}')
        else:
            print(f'        ❌ No email found')
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

        # Normalize to 5
        max_score = 18 # adjust if weights increase
        normalized = min(5, (raw_score / max_score) * 5)
        return round(normalized, 2)

    def update_score_with_email_and_reviews(self, email_weight=0.3, review_weight=0.1, original_score_weight=0.6):
        """
        Updates the lead score by incorporating email quality and review sentiment.
        This is now called automatically during __init__ before threshold checks.
        """
        # Original raw score
        original_score = self.lead_score or self.score_place()

        # Score emails
        if self.emails:
            email_scores = [score_email(e) for e in self.emails]
            best_email_score = max(email_scores)
        else:
            best_email_score = 1  # minimal if no email

        # Score reviews (first 5)
        if self.reviews:
            avg_review_score, review_scores = score_reviews_list(self.reviews)
            avg_review_score = 6 - avg_review_score # invert so more bad reviews better the lead
        else:
            avg_review_score = 3  # neutral if no reviews

        # Combine all scores
        combined_score = (
            original_score * original_score_weight + 
            best_email_score * email_weight +
            avg_review_score * review_weight
        )

        # Normalize to 1-5
        self.lead_score = round(min(max(combined_score, 1), 5), 2)
        return self.lead_score