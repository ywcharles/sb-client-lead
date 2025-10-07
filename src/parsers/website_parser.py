import requests
import os
import re
from collections import deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright


EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
ROLE_BASED_PREFIXES = {
    "info",
    "support",
    "help",
    "admin",
    "sales",
    "contact",
    "office",
    "billing",
    "customerservice",
    "noreply",
    "no-reply",
    "service",
    "team",
}


def filter_emails(emails):
    output_emails = []
    for mail in emails:
        name = mail.split("@")[0]
        if name not in ROLE_BASED_PREFIXES and mail != '':
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

    def crawl_website(url: str, max_pages=5):
        relevant_keywords = [
            "about",
            "who-we-are",
            "our-story",
            "company",
            "team",
            "contact",
            "careers",
            "jobs",
            "services",
            "products",
            "faq",
            "help",
            "support",
            "blog",
            "news",
        ]
        html_contents = []
        visited = set()
        q = deque([url])
        domain = urlparse(url).netloc

        while q and len(html_contents) < max_pages:
            curr_page_url = q.popleft()
            try:
                response = requests.get(curr_page_url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")

                for a_tag in soup.find_all("a", href=True):
                    full_url = urljoin(curr_page_url, a_tag["href"])
                    same_domain = domain in urlparse(full_url).netloc
                    page_not_visited = full_url not in visited
                    relevant_page = any(keyword in full_url.lower() for keyword in relevant_keywords)
                    if same_domain and page_not_visited  and relevant_page:
                        q.append(full_url)

                html_contents.append(soup.text)

            except Exception:
                return "Failed to extract HTML contents"

            visited.add(curr_page_url)
        return html_contents

    def extract_html_contents(url: str):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            return str(soup)

        except Exception:
            return "Failed to extract HTML contents"

    @staticmethod
    def take_screenshot(url, full_page=True): # TODO Delete screenshot once UI report is done
        try:
            # Make sure screenshot folder exists
            screenshot_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000)

                output_file = os.path.join(screenshot_dir, f"temp_screenshot.png")

                page.screenshot(path=output_file, full_page=full_page)
                browser.close()

            return output_file
        except Exception as e:
            return f"Failed to take screenshot: {e}"
