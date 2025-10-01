from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import os

load_dotenv()

OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
class LeadsAgent:
    def __init__(self):
        self.base_model = ChatOpenAI(model="gpt-4o", api_key = OPEN_AI_API_KEY)