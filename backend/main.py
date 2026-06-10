from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from groq import RateLimitError, APIError
import io, json

from backend.auth import register_user, login_user, get_current_user
from backend.generator import generate_curriculum
from backend.resources import get_resources
from backend.pdf_generator import build_curriculum_pdf
from backend.educator_generator import generate_educator_curriculum
from backend.educator_pdf import build_educator_pdf
from backend.database import save_course, get_courses, get_course, delete_course

app = FastAPI(title="EduSync")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


# ── Auth ───────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username:         str
    email:            str
    password:         str
    confirm_password: str
    role:             str = "student"


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/auth/register")
def register(body: RegisterRequest):
    if body.password != body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    return register_user(body.username.strip(), body.email.strip(), body.password, body.role)


@app.post("/auth/login")
def login(body: LoginRequest):
    return login_user(body.username.strip(), body.password)


# ── Curriculum ─────────────────────────────────────────────────────────────────

class CurriculumRequest(BaseModel):
    topic:    str
    level:    str
    duration: int
    goal:     str


@app.post("/generate")
def generate(req: CurriculumRequest, user: dict = Depends(get_current_user)):
    try:
        return generate_curriculum(req.topic, req.level, req.duration, req.goal)
    except (RateLimitError, APIError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitError) else 502, detail=str(e))


@app.get("/resources")
def resources(topic: str, level: str, user: dict = Depends(get_current_user)):
    try:
        return get_resources(topic, level)
    except (RateLimitError, APIError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitError) else 502, detail=str(e))


class PDFRequest(BaseModel):
    curriculum: dict
    topic:      str
    level:      str
    duration:   int
    goal:       str


@app.post("/download-pdf")
def download_pdf(req: PDFRequest, user: dict = Depends(get_current_user)):
    pdf_bytes = build_curriculum_pdf(req.curriculum, {
        "topic": req.topic, "level": req.level,
        "duration": req.duration, "goal": req.goal
    })
    filename = f"EduSync_{req.topic.replace(' ','_')}_Curriculum.pdf"
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


# ── Educator ───────────────────────────────────────────────────────────────────

class EducatorRequest(BaseModel):
    subject:        str
    level:          str
    semesters:      int
    weekly_hours:   int
    industry_focus: str


@app.post("/educator/generate")
def educator_generate(req: EducatorRequest, user: dict = Depends(get_current_user)):
    try:
        return generate_educator_curriculum(
            req.subject, req.level, req.semesters,
            req.weekly_hours, req.industry_focus
        )
    except (RateLimitError, APIError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitError) else 502, detail=str(e))


class EducatorPDFRequest(BaseModel):
    curriculum:     dict
    subject:        str
    level:          str
    semesters:      int
    weekly_hours:   int
    industry_focus: str


@app.post("/educator/download-pdf")
def educator_download_pdf(req: EducatorPDFRequest, user: dict = Depends(get_current_user)):
    pdf_bytes = build_educator_pdf(req.curriculum, {
        "subject": req.subject, "level": req.level,
        "semesters": req.semesters, "weekly_hours": req.weekly_hours,
        "industry_focus": req.industry_focus
    })
    filename = f"EduSync_{req.subject.replace(' ','_')}_Educator_Curriculum.pdf"
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


# ── Saved Courses (SQLite) ──────────────────────────────────────────────────────

class SaveCourseRequest(BaseModel):
    course_id: str
    title:     str
    subject:   str
    level:     str
    role_type: str
    meta:      dict
    full_data: dict


@app.post("/courses/save")
def course_save(req: SaveCourseRequest, user: dict = Depends(get_current_user)):
    save_course(
        user_id=user["id"], course_id=req.course_id,
        title=req.title, subject=req.subject, level=req.level,
        role_type=req.role_type, meta=req.meta, full_data=req.full_data
    )
    return {"message": "Course saved"}


@app.get("/courses")
def courses_list(user: dict = Depends(get_current_user)):
    rows = get_courses(user["id"])
    for r in rows:
        r["meta"]      = json.loads(r.get("meta_json") or "{}")
        r["full_data"] = json.loads(r.get("full_json") or "{}")
        r.pop("meta_json", None)
        r.pop("full_json", None)
    return rows


@app.get("/courses/{course_id}")
def course_detail(course_id: str, user: dict = Depends(get_current_user)):
    row = get_course(user["id"], course_id)
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    row["meta"]      = json.loads(row.get("meta_json") or "{}")
    row["full_data"] = json.loads(row.get("full_json") or "{}")
    row.pop("meta_json", None)
    row.pop("full_json", None)
    return row


@app.delete("/courses/{course_id}")
def course_delete(course_id: str, user: dict = Depends(get_current_user)):
    delete_course(user["id"], course_id)
    return {"message": "Course deleted"}


# ── Week Quiz ─────────────────────────────────────────────────────────────────

class QuizRequest(BaseModel):
    week:   int
    title:  str
    topics: list[str]
    level:  str


@app.post("/quiz/generate")
def generate_week_quiz(req: QuizRequest, user: dict = Depends(get_current_user)):
    from backend.generator import client, MODEL
    prompt = (
        f"Generate 5 multiple-choice quiz questions to assess a {req.level} student's understanding "
        f"of Week {req.week}: '{req.title}'.\n"
        f"Topics covered: {', '.join(req.topics)}.\n"
        "Return a JSON array only — no extra text:\n"
        "[{\"question\":\"...\",\"options\":[\"A\",\"B\",\"C\",\"D\"],\"answer\":0,\"explanation\":\"...\"}]"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        text = resp.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        return json.loads(text.strip())
    except (RateLimitError, APIError) as e:
        raise HTTPException(status_code=429 if isinstance(e, RateLimitError) else 502, detail=str(e))


# ── Frontend pages ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse(FRONTEND / "login.html")


@app.get("/{page}")
def pages(page: str):
    f = FRONTEND / f"{page}.html"
    if f.exists():
        return FileResponse(f)
    return FileResponse(FRONTEND / "login.html")
