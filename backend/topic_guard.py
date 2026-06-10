import os
from groq import Groq
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"

# Topics that are clearly academic/educational subjects
_ALLOWED_KEYWORDS = {
    # Sciences & Engineering
    "programming","coding","software","algorithm","data structure","database",
    "machine learning","deep learning","artificial intelligence","ai","ml","nlp",
    "computer","network","cybersecurity","cloud","devops","web","mobile","api",
    "python","java","javascript","react","angular","node","sql","nosql",
    "mathematics","statistics","calculus","algebra","geometry","physics",
    "chemistry","biology","science","engineering","electronics","robotics",
    # Business & Management
    "management","marketing","finance","accounting","economics","business",
    "entrepreneurship","mba","leadership","strategy","hr","human resource",
    # Humanities & Social Sciences
    "history","geography","psychology","sociology","philosophy","literature",
    "english","language","communication","journalism","law","political",
    # Design & Arts
    "design","graphic","ux","ui","animation","music","art","architecture",
    # Health
    "medical","nursing","health","anatomy","pharmacology","nutrition",
    # General Education
    "education","teaching","curriculum","course","subject","skill","learning",
    "study","academic","university","college","school","degree","certification",
}


def validate_education_topic(topic: str) -> None:
    """
    Two-layer check:
    1. Fast keyword check (no API call needed)
    2. AI classification for borderline cases

    Raises HTTPException(400) if topic is not education-related.
    """
    topic_lower = topic.lower().strip()

    # Layer 1: keyword allowlist — if any known academic keyword present, allow immediately
    if any(kw in topic_lower for kw in _ALLOWED_KEYWORDS):
        return

    # Layer 2: AI classification for topics not caught by keywords
    prompt = f"""You are a strict educational content classifier for EduSync, an academic curriculum platform.

Determine if the following topic is a valid academic subject, technical skill, or professional learning area that belongs in a university/college/professional curriculum.

Topic: "{topic}"

Reply with ONLY one word: YES or NO

- YES if it is: an academic subject, technical skill, programming language, science, engineering, business, design, medical, humanities, language, or any legitimate educational domain
- NO if it is: a request for personal advice, entertainment, news, jokes, cooking recipes, sports commentary, political opinions, adult content, harmful content, or anything unrelated to formal education
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=5,
        )
        answer = response.choices[0].message.content.strip().upper()
        if not answer.startswith("YES"):
            raise HTTPException(
                status_code=400,
                detail=f'"{topic}" is not a valid academic subject or skill. '
                       f"EduSync only generates curricula for educational topics such as "
                       f"programming, mathematics, science, business, design, and other academic domains."
            )
    except HTTPException:
        raise
    except Exception:
        # If classification itself fails (rate limit etc.), fall through and allow
        return
