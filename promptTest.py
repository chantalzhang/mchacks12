import openai as oai
from dotenv import load_dotenv
import os

load_dotenv()
oai.api_key = os.getenv("OPENAI_API_KEY")

print(oai.api_key)
