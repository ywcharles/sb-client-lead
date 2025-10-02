from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv

from parsers.website_parser import WebsiteParser as wp

import os
import base64
from place import Place

load_dotenv()

OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")


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
                ]
            )

            return resp.output_text

        except Exception as e:
            return {
                "ui_report": f"Failed to generate UI report: {e}",
                "screenshot": None,
            }
