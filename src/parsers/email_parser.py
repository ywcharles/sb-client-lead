import requests
from bs4 import BeautifulSoup
import re

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

class EmailParser:
    @staticmethod
    def extract_emails(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            emails = set()

            # 1. Look for mailto: links
            for a in soup.find_all("a", href=True):
                if a["href"].startswith("mailto:"):
                    email = a["href"].replace("mailto:", "").split("?")[0]
                    emails.add(email)

            # 2. Regex fallback
            if not emails:
                text = soup.get_text(" ", strip=True)
                found = re.findall(EMAIL_REGEX, text)
                # Clean bad matches
                cleaned = [e.strip(" ,;:.") for e in found if e and "@" in e]
                emails.update(cleaned)

            return list(emails)

        except Exception:
            return []
