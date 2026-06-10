import os
import json
import time
from groq import Groq, RateLimitError
from dotenv import load_dotenv
from pathlib import Path
from backend.topic_guard import validate_education_topic

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"
PROMPTS = Path(__file__).parent / "prompts"


def _call(prompt: str, retries: int = 4, wait: int = 65) -> dict:
    """Call Groq with automatic retry on rate-limit errors."""
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=8000,
            )
            text = response.choices[0].message.content.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except RateLimitError:
            if attempt < retries - 1:
                time.sleep(wait)
            else:
                raise
        except json.JSONDecodeError as e:
            if attempt < retries - 1:
                time.sleep(10)
            else:
                raise ValueError(f"AI returned invalid JSON: {e}")


def _placeholder_weekly(sem_title: str, weekly_hours: int) -> dict:
    """Fallback weekly plan when AI call fails."""
    return {
        "weekly_plan": [
            {
                "week": w,
                "topic": f"Week {w} — {sem_title}",
                "subtopics": ["Core concepts", "Practical examples", "Review"],
                "teaching_method": "Lecture",
                "hours": weekly_hours,
                "activities": "Lecture, discussion and Q&A",
                "assessment": "None"
            } for w in range(1, 17)
        ],
        "semester_assessments": {
            "assignments":   [{"title": "Assignment 1", "week_due": 5,  "description": "Written assignment", "marks": 10},
                              {"title": "Assignment 2", "week_due": 12, "description": "Written assignment", "marks": 10}],
            "quizzes":       [{"title": "Quiz 1", "week": 4,  "topics": "Weeks 1-3", "marks": 5},
                              {"title": "Quiz 2", "week": 10, "topics": "Weeks 4-9", "marks": 5}],
            "projects":      [{"title": "Semester Project", "type": "Group", "description": "Industry-aligned project", "marks": 25, "deliverables": ["Report", "Presentation"]}],
            "lab_exercises": [{"title": "Lab 1", "week": 3, "description": "Practical lab", "tools": ["relevant tools"]},
                              {"title": "Lab 2", "week": 8, "description": "Practical lab", "tools": ["relevant tools"]}]
        },
        "mark_distribution": {"assignments": 20, "quizzes": 15, "midterm": 25, "project": 30, "lab": 10}
    }


def generate_educator_curriculum(
    subject: str, level: str, semesters: int,
    weekly_hours: int, industry_focus: str
) -> dict:

    # ── Guard: reject non-educational topics ─────────────────────────────
    validate_education_topic(subject)

    # ── Phase 1: Course overview (small, fast) ────────────────────────────
    overview_prompt = (PROMPTS / "educator_overview_prompt.txt").read_text().format(
        subject=subject, level=level, semesters=semesters,
        weekly_hours=weekly_hours, industry_focus=industry_focus
    )
    data = _call(overview_prompt)

    # ── Phase 2: Weekly plan per semester with delay between calls ─────────
    weekly_tpl = (PROMPTS / "educator_weekly_prompt.txt").read_text()

    for i, sem in enumerate(data.get("semesters", [])):
        # Wait between calls to respect rate limits (except first call)
        if i > 0:
            time.sleep(20)

        sem_num   = sem.get("semester", i + 1)
        sem_title = sem.get("title", f"Semester {sem_num}")
        sem_focus = sem.get("focus", "")
        sem_los   = ", ".join(sem.get("learning_outcomes", []))

        prompt = weekly_tpl.format(
            subject=subject, level=level, industry_focus=industry_focus,
            weekly_hours=weekly_hours, semester=sem_num,
            sem_title=sem_title, sem_focus=sem_focus, sem_los=sem_los
        )

        try:
            weekly = _call(prompt)
            sem["weekly_plan"]            = weekly.get("weekly_plan", [])
            sem["semester_assessments"]   = weekly.get("semester_assessments", {})
            sem["mark_distribution"]      = weekly.get("mark_distribution", {})
        except Exception:
            fallback = _placeholder_weekly(sem_title, weekly_hours)
            sem["weekly_plan"]          = fallback["weekly_plan"]
            sem["semester_assessments"] = fallback["semester_assessments"]
            sem["mark_distribution"]    = fallback["mark_distribution"]

    return data
