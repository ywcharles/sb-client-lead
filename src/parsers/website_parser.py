import requests
from bs4 import BeautifulSoup
import re

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
ROLE_BASED_PREFIXES = {
    "info", "support", "help", "admin", "sales", "contact", "office",
    "billing", "customerservice", "noreply", "no-reply", "service", "team"
}

def filter_emails(emails):
        output_emails = []
        for mail in emails:
            name = mail.split("@")[0]
            if name not in ROLE_BASED_PREFIXES:
                output_emails.append(mail)

        return output_emails

class WebsiteParser:
    def extract_emails(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            emails = set()

            # 1. mailto links
            for a in soup.find_all("a", href=True):
                if a["href"].lower().startswith("mailto:"):
                    email = a["href"].replace("mailto:", "").split("?")[0]
                    email = email.strip(" ,;:.()[]<>\"'")
                    emails.add(email)

            # 2. regex fallback
            text = soup.get_text(" ", strip=True)
            found = re.findall(EMAIL_REGEX, text)
            cleaned = [e.strip(" ,;:.()[]") for e in found if "@" in e]
            emails.update(cleaned)

            emails = filter_emails(emails)
            
            return list(set(emails))

        except Exception:
            return []
        
    def extract_html_contents(url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            return soup.text

        except Exception:
            return "Failed to extract HTML contents"