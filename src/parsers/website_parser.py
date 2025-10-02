import requests
from bs4 import BeautifulSoup
import re

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

class WebsiteParser:
    @staticmethod
    def extract_emails(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            emails = set()

            # 1. mailto: links
            for a in soup.find_all("a", href=True):
                if a["href"].lower().startswith("mailto:"):
                    email = a["href"].replace("mailto:", "").split("?")[0]
                    email = email.strip(" ,;:.()[]<>\"'")  
                    emails.add(email)


            # 2. regex fallback
            if not emails:
                text = soup.get_text(" ", strip=True)
                found = re.findall(EMAIL_REGEX, text)
                cleaned = [e.strip(" ,;:.()[]") for e in found if "@" in e]
                emails.update(cleaned)

            return list(emails)

        except Exception:
            return []
        
    def extract_html_contents(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            return soup.text

        except Exception:
            return "Failed to extract HTML contents"