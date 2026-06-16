# EduSync 🎓
Generative AI–Powered Curriculum Design System

## Setup

### 1. Install dependencies
```bash
cd CurricuForge
pip install -r requirements.txt
```

### 2. Configure API keys
Edit `.env` and add your keys:
```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=any_random_secret_string
```

Get a free Groq API key at: https://console.groq.com/keys

### 3. Run the server
```bash
uvicorn backend.main:app --reload
```

### 4. Open the app
Visit: http://localhost:8000

---

## Project Structure
```
EduSync/
├── frontend/
│   ├── login.html       # Auth page (login + register)
│   ├── home.html        # Landing page describing the app
│   ├── generate.html    # AI curriculum generator
│   ├── about.html       # About the project & tech stack
│   ├── contact.html     # Contact form
│   ├── css/style.css    # Shared dark-theme styles
│   └── js/app.js        # Auth, nav, API helpers
├── backend/
│   ├── main.py          # FastAPI app + routes
│   ├── auth.py          # JWT login/register
│   ├── generator.py     # Gemini AI curriculum generation
│   ├── resources.py     # AI resource suggestions
│   ├── database.py      # In-memory user store
│   └── prompts/         # AI prompt templates
├── requirements.txt
└── .env                 # API keys (do not commit)
```

## API Endpoints
| Method | Endpoint          | Description                    |
|--------|-------------------|--------------------------------|
| POST   | /auth/register    | Register a new user            |
| POST   | /auth/login       | Login, returns JWT token       |
| POST   | /generate         | Generate curriculum (auth req) |
| GET    | /resources        | Get resource list (auth req)   |
