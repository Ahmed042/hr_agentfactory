from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.ai.brain import ai_brain
from app.models.candidate import Candidate
from app.models.ai_action import AIAction
from app.models.activity_log import ActivityLog
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ScreenRequest(BaseModel):
    candidate_id: int
    cv_text: str


class EmailGenRequest(BaseModel):
    candidate_id: int
    email_type: str
    context: Optional[dict] = {}


class SentimentRequest(BaseModel):
    text: str


@router.post("/screen-candidate")
async def screen_candidate(data: ScreenRequest, db: Session = Depends(get_db)):
    """AI screens a candidate's CV"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        return {"error": "Candidate not found"}

    result = await ai_brain.analyze_candidate(data.cv_text, candidate.job_role or "General")

    # Update candidate
    candidate.ai_score = result.get("score", 0)
    candidate.ai_reasoning = result.get("reasoning", "")
    if result.get("decision") == "reject":
        candidate.status = "rejected"
        candidate.stage = "rejected"
    else:
        candidate.status = "screening"
        candidate.stage = "screening"

    # Log action
    action = AIAction(
        candidate_id=data.candidate_id,
        action_type="cv_screening",
        reasoning=result.get("reasoning", ""),
        action_metadata=result,
    )
    db.add(action)

    log = ActivityLog(
        entity_type="candidate",
        entity_id=data.candidate_id,
        action="ai_screened",
        description=f"AI scored {result.get('score', 0)}/100 - {result.get('decision', 'unknown')}",
        actor="AI",
    )
    db.add(log)
    db.commit()

    return result


@router.post("/generate-email")
async def generate_email(data: EmailGenRequest, db: Session = Depends(get_db)):
    """AI generates an email for a candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        return {"error": "Candidate not found"}

    context = {
        "name": candidate.name or candidate.email.split("@")[0],
        "job_role": candidate.job_role,
        **data.context,
    }

    email_content = await ai_brain.generate_email(context, data.email_type)
    return {"email_content": email_content, "email_type": data.email_type}


@router.post("/suggest-questions")
async def suggest_questions(job_role: str, cv_summary: str = ""):
    """AI suggests interview questions"""
    questions = await ai_brain.suggest_interview_questions(job_role, cv_summary)
    return {"questions": questions}


@router.post("/analyze-sentiment")
async def analyze_sentiment(data: SentimentRequest):
    """AI analyzes email/text sentiment"""
    result = await ai_brain.analyze_sentiment(data.text)
    return result
