
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

print("\nAvailable Gemini models:\n")

for model in client.models.list():

    actions = getattr(model, "supported_actions", [])

    if "generateContent" in actions:
        print(model.name)
