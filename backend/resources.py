import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def get_resources(topic: str, level: str) -> list:
    prompt = f"""List the 8 best learning resources for "{topic}" at {level} level.
Return a JSON array only:
[
  {{
    "title": "...",
    "type": "video|article|book|course|tool",
    "url": "...",
    "platform": "...",
    "description": "...",
    "free": true
  }}
]
Only return valid JSON, no extra text."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text.strip())
