from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_tables, SessionLocal
from app.core.auth import create_default_admin
from app.api.routes import candidates, employees, departments, payroll, interviews, job_postings, analytics, document_templates, notes, ai, auth, emails, public, candidate_actions, leaves, documents, webhooks
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HR AgentFactory",
    description="Enterprise AI-Powered Recruitment Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully")

    # Auto-create admin user
    db = SessionLocal()
    try:
        create_default_admin(db)
    finally:
        db.close()


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "HR AgentFactory",
        "version": "2.0.0",
    }


# Auth (public)
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

# Core routes
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])
app.include_router(payroll.router, prefix="/api/payroll", tags=["Payroll"])

# Feature routes
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(job_postings.router, prefix="/api/job-postings", tags=["Job Postings"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(document_templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])

# Email routes
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])

# Candidate Actions
app.include_router(candidate_actions.router, prefix="/api/actions", tags=["Candidate Actions"])

# Leave & Document routes
app.include_router(leaves.router, prefix="/api/leaves", tags=["Leaves"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])

# Webhooks
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])

# Public routes (no auth)
app.include_router(public.router, prefix="/public", tags=["Public"])
