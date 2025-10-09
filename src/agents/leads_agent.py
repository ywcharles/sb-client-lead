from openai import OpenAI

from parsers.website_parser import WebsiteParser as wp

import base64
from tools.keys import get_secret

OPEN_AI_API_KEY = get_secret("OPENAI_API_KEY")


class LeadsAgent:
    def __init__(self):
        self.base_model = OpenAI(api_key=OPEN_AI_API_KEY)

    def generate_ui_report(self, url: str):
        """
        Analyze only UI improvements for the given website.
        Saves a screenshot of the site and sends it to the AI for analysis.
        """
        try:
            # Take screenshot
            screenshot_path = wp.take_screenshot(url)
            with open(screenshot_path, "rb") as image_file:
                image_64 = base64.b64encode(image_file.read()).decode("utf-8")
            # Prompt for UI analysis only
            prompt = """
    You are an experienced web developer and UI designer.

    Analyze the website screenshot.
    Focus only on **UI improvements** (design, layout, accessibility, usability).
    If there are no UI improvements, simply output "NO IMPROVEMENTS".
    Consider if the UI is oudated with the newest UI trends, as well if the branding is cohesive

    Keep response concise (max 200 words). Be specific and actionable.
    """

            resp = self.base_model.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{image_64}",
                            },
                        ],
                    }
                ],
            )

            return resp.output_text

        except Exception as e:
            print(e)

    def generate_business_brief(self, url: str):
        """
        Analyze business website and generates a brief about it
        """
        try:
            page_contents = wp.crawl_website(url)

            prompt = f"""
You are a consultant at a company that provides automation (operations, sales, support), website redesign, organizational and process consulting, and bookkeeping/accounting services. 

I will give you raw text content scraped from a potential client’s website. 

Your task:
1. Ignore irrelevant text like navigation menus, cookie notices, or repeated boilerplate.  
2. Identify what the business does, their industry, and their positioning from the text.  
3. Write a concise, personalized brief (1 short paragraph) that:  
   - Provides context about the client’s business.  
   - Suggests quick wins or opportunities for automation, website improvements, or consulting.  
   - Highlights anything notable or relevant based on their website.  

Here is the content:
{page_contents}

Keep response concise (max 200 words) but still be specific.
    """

            resp = self.base_model.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                        ],
                    }
                ],
            )

            return resp.output_text

        except Exception as e:
            print(e)

    def generate_pain_points(self, brief: str, ui_report: str, reviews: list):
        """
        Generate a pain point report using a precomputed brief, UI report, and reviews.
        """
        try:
            google_map_reviews = "\n".join(
                [f"Review {idx + 1}: {review['text']['text']}" for idx, review in enumerate(reviews)]
            )

            prompt = f"""
You are a consultant at a company that provides automation (operations, sales, support), website redesign, organizational/process consulting, and bookkeeping/accounting services.  

I will provide you with three types of input:  
1. A brief about the business.  
2. An evaluation of their website’s UI/UX.  
3. A sample of 5 Google Maps reviews.  

Your task is to analyze this information and produce a structured report that:  

1. **Identifies key pain points** the business might be facing (e.g., outdated website design, inefficient operations, negative customer experiences, lack of automation, weak online presence, poor financial processes, etc.).  
2. **Explains the impact** of each pain point on the business (e.g., lost customers, wasted staff hours, reduced credibility, slower sales cycle).  
3. **Recommends solutions** that our consultancy can provide to address these pain points, showing how our services (automation, redesign, consulting, bookkeeping) can directly help.  

Format the output as:  

**Business Pain Point Report**  
- Pain Point 1: [Short description]  
  - Impact: [Explain business consequence]  
  - How We Can Help: [Relevant service + brief explanation]  

- Pain Point 2: [Short description]  
  - Impact: [Explain business consequence]  
  - How We Can Help: [Relevant service + brief explanation]  

Keep the language clear, professional, and focused on insights that can be turned into client-facing outreach.  

Brief:  
{brief}  

Website UI Report:  
{ui_report}  

Google Maps Reviews:  
{google_map_reviews}  

Keep response concise (max 150 words). Be specific and actionable.
"""

            resp = self.base_model.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
            )

            return resp.output_text

        except Exception as e:
            print(e)

    def generate_personalized_email(self, business_name: str, brief: str, pain_point_report: str):
        """
        Generate a short personalized cold email:
        - 1 personalization-driven opening line
        - 2–3 tailored benefits (solutions to pain points)
        - 1 simple CTA
        """
        try:
            prompt = f"""
You are a professional B2B sales copywriter.

Write a short, concrete cold outreach email for {business_name}.
Use the following information:

Brief about business:
{brief}

Business Pain Point Report:
{pain_point_report}

Format:
- 1 opening line that shows personalization and context.
- 2–3 tailored benefits based on their pain points (from our services: automation, redesign, consulting, bookkeeping).
- 1 simple CTA to continue the conversation (like scheduling a quick call).

Tone: professional but approachable. No fluff, no jargon. Keep it under 120 words.
"""

            resp = self.base_model.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
            )

            return resp.output_text

        except Exception as e:
            print(e)
