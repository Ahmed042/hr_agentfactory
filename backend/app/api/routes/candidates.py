from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_service import candidate_service
from app.models.candidate import Candidate
from app.models.activity_log import ActivityLog
from pydantic import BaseModel, EmailStr
from typing import Optional, List

router = APIRouter()


class CandidateCreate(BaseModel):
    email: EmailStr
    job_role: str
    name: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    expected_salary: Optional[int] = None
    skills: Optional[List[str]] = None


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    job_role: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    expected_salary: Optional[int] = None
    skills: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class CandidateResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    job_role: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    ai_score: Optional[int] = None
    ai_reasoning: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    expected_salary: Optional[int] = None
    skills: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    has_cv: Optional[bool] = False
    has_cnic: Optional[bool] = False
    has_certificates: Optional[bool] = False
    has_references: Optional[bool] = False
    applied_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=dict)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
):
    result = await candidate_service.create_candidate(
        db=db,
        email=candidate.email,
        job_role=candidate.job_role,
        name=candidate.name,
        phone=candidate.phone,
        source=candidate.source,
        location=candidate.location,
        experience_years=candidate.experience_years,
        expected_salary=candidate.expected_salary,
        skills=candidate.skills,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/")
def get_candidates(
    status: str = None,
    stage: str = None,
    job_role: str = None,
    search: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(Candidate)
    if status:
        query = query.filter(Candidate.status == status)
    if stage:
        query = query.filter(Candidate.stage == stage)
    if job_role:
        query = query.filter(Candidate.job_role == job_role)
    if search:
        query = query.filter(
            (Candidate.email.ilike(f"%{search}%")) |
            (Candidate.name.ilike(f"%{search}%")) |
            (Candidate.job_role.ilike(f"%{search}%"))
        )
    return query.order_by(Candidate.applied_at.desc()).all()


@router.get("/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.put("/{candidate_id}")
def update_candidate(candidate_id: int, data: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    old_status = candidate.status

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(candidate, key, value)

    # Log status changes
    if data.status and data.status != old_status:
        log = ActivityLog(
            entity_type="candidate",
            entity_id=candidate_id,
            action="status_changed",
            description=f"Status changed from {old_status} to {data.status}",
            actor="admin",
        )
        db.add(log)

    db.commit()
    db.refresh(candidate)
    return candidate


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted"}
