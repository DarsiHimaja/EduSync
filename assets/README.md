# 🎓 EduSync – Generative AI Powered Curriculum Design System

<div align="center">

### Transforming Curriculum Design with Artificial Intelligence

EduSync is an intelligent AI-powered educational platform that automates curriculum creation, generates personalized learning plans, and provides AI-driven educational resources using Groq Llama 3.3 70B.

</div>

---

# 📖 Overview

Traditional curriculum development requires educators to manually design course structures, learning outcomes, assessments, projects, and learning resources. This process can be time-consuming and difficult to keep aligned with modern industry requirements.

EduSync solves this challenge by integrating **Generative AI** with modern full-stack technologies. Using the **Groq API** and **Llama 3.3 70B Large Language Model**, the system automatically generates high-quality, structured, and industry-oriented curricula.

The platform supports two major user roles:

## 👨‍🏫 Educators

Educators can:

- Create complete AI-generated curricula
- Generate semester-wise syllabus
- Generate Bloom's Taxonomy based learning outcomes
- Create assignments, quizzes, and examinations
- Generate mini and capstone projects
- Perform skill mapping and curriculum gap analysis
- Export professional curriculum reports as PDFs

---

## 👨‍🎓 Students

Students can:

- Create personalized weekly study plans
- Receive AI-generated learning recommendations
- Access educational resources
- Practice quizzes and assessments
- Track learning progress through analytics

---

# ✨ Key Features

## 🤖 AI Curriculum Generation

- Course overview generation
- Semester-wise syllabus creation
- Learning outcome generation
- Assessment creation
- Assignment generation
- Mini and capstone project suggestions
- Resource recommendations
- Skill mapping

---

## 🔍 Curriculum Analysis

The system can analyze curriculum quality and identify:

- Missing concepts
- Outdated topics
- Industry skill gaps
- Improvement suggestions

---

## 📄 PDF Export

Generated curricula can be converted into professional PDF reports that include:

- Course details
- Semester plans
- Learning outcomes
- Assessments
- Projects
- Educational resources

---

# 🏛 System Architecture

EduSync follows a multi-layered client-server architecture.

## Architecture Diagram

![EduSync System Architecture](assets/system-architecture.png)

### Components

### 1. User Layer
- Educators
- Students

### 2. Web Application Layer
Developed using:

- HTML5
- CSS3
- JavaScript
- Bootstrap

Provides a responsive and user-friendly interface.

---

### 3. FastAPI Backend

Responsible for:

- REST API development
- Business logic
- Authentication
- AI communication
- Database operations

---

### 4. Authentication Module

Uses JWT tokens for:

- Secure registration
- User login
- Session management
- Protected API access

---

### 5. AI Processing Layer

Powered by:

- Groq API
- Llama 3.3 70B

Performs:

- Curriculum understanding
- Course analysis
- Learning outcome generation
- Assessment creation
- Resource recommendation

---

### 6. SQLite Database

Stores:

- User accounts
- Curriculum history
- Generated syllabi
- Assessments
- Learning plans
- Educational resources

---

### 7. PDF Export Module

Generates downloadable professional curriculum reports.

---

# 🔄 Curriculum Generation Workflow

The following sequence diagram illustrates how curriculum generation works.

## Sequence Diagram

![Curriculum Workflow](assets/sequence-diagram.png)

### Workflow Steps

1. Educator enters course details.
2. Frontend sends the request to FastAPI.
3. JWT authentication and input validation are performed.
4. Backend creates an AI prompt.
5. Prompt is sent to Groq API.
6. Llama 3.3 70B generates the curriculum.
7. Backend structures the AI response.
8. Data is stored in SQLite.
9. Curriculum is displayed on the dashboard.
10. User can export the curriculum as PDF.

---

# 🧠 AI Curriculum Generation Engine

The AI engine converts user input into a complete academic curriculum.

## AI Pipeline Diagram

![AI Curriculum Engine](assets/ai-generation-engine.png)

---

## Input Parameters

The educator provides:

- Course Name
- Educational Level
- Number of Semesters
- Weekly Hours
- Total Credits
- Technology Specialization

---

## AI Processing

The LLM performs:

- Course analysis
- Difficulty understanding
- Semester planning
- Topic sequencing
- Learning outcome generation
- Assessment generation
- Resource identification
- Skill mapping

---

## Generated Output

The final curriculum contains:

- Course overview
- Semester-wise syllabus
- Learning outcomes
- Assignments
- Quizzes
- Exams
- Mini projects
- Capstone projects
- Educational resources
- Skill gap analysis
- Downloadable PDF reports

---

# 🛠 Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

---

## Backend

- Python
- FastAPI
- Uvicorn

---

## Artificial Intelligence

- Groq API
- Llama 3.3 70B

---

## Database

- SQLite

---

## Security

- JWT Authentication
- Password Encryption
- Protected API Routes

---

# 📁 Project Structure

```
EduSync/
│
├── assets/
│   ├── system-architecture.png
│   ├── sequence-diagram.png
│   └── ai-generation-engine.png
│
├── frontend/
│   ├── login.html
│   ├── home.html
│   ├── generate.html
│   ├── about.html
│   ├── contact.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── generator.py
│   ├── resources.py
│   ├── database.py
│   └── prompts/
│
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Installation & Setup

## 1. Clone Repository

```bash
git clone <repository-url>
cd EduSync
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configure API Keys

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_random_secret_key
```

Get a free Groq API key:

https://console.groq.com/keys

---

# ▶️ Running the Application

Start the FastAPI development server:

```bash
uvicorn backend.main:app --reload
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

# 🔐 Authentication Flow

1. User registers as Educator or Student.
2. Credentials are securely stored.
3. User logs into the system.
4. Backend generates a JWT token.
5. Protected APIs require a valid JWT token.

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |
| POST | `/generate` | Generate AI curriculum |
| GET | `/resources` | Retrieve educational resources |
| GET | `/assessment` | Get AI-generated assessments |
| GET | `/learning-plan` | Generate personalized study plans |

---

# 🚀 Future Scope

Future improvements include:

- Multi-model AI support
- Multilingual curriculum generation
- Cloud database migration
- Learning Management System integration
- Real-time educator collaboration
- Mobile application development
- Advanced analytics dashboards
- Adaptive AI-based assessments

---

# 🎯 Learning Outcomes

Through EduSync, developers gain experience in:

- Generative AI integration
- Prompt engineering
- FastAPI backend development
- REST API design
- JWT authentication
- Database management
- Full-stack web development
- AI-powered educational systems

---

# 📜 License

This project is developed for educational and research purposes.

---

<div align="center">

## 🌟 EduSync – Building the Future of Intelligent Education with AI

Powered by Groq • Llama 3.3 70B • FastAPI • SQLite

</div>
