import os
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from backend.topic_guard import validate_education_topic

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

PROMPT_PATH = Path(__file__).parent / "prompts" / "curriculum_prompt.txt"


def generate_curriculum(topic: str, level: str, duration: int, goal: str) -> dict:
    validate_education_topic(topic)
    prompt_template = PROMPT_PATH.read_text()
    prompt = prompt_template.format(
        topic=topic, level=level, duration=duration, goal=goal
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text.strip())
