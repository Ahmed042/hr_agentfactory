from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job_posting import JobPosting
from app.models.activity_log import ActivityLog
from app.ai.brain import ai_brain
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class JobPostingCreate(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: str = "full_time"
    experience_level: str = "mid"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    benefits: Optional[str] = None
    skills_required: Optional[List[str]] = None
    is_remote: bool = False


class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    benefits: Optional[str] = None
    skills_required: Optional[List[str]] = None
    status: Optional[str] = None
    is_remote: Optional[bool] = None


@router.post("/generate-description")
async def generate_job_description(title: str, department: str = ""):
    """AI generates full job description from just title + department"""
    if not ai_brain._is_available():
        return {
            "title": title,
            "department": department,
            "description": f"We are looking for a talented {title} to join our {department or 'team'}.",
            "responsibilities": "- Lead projects and initiatives\n- Collaborate with cross-functional teams\n- Drive results and innovation",
            "required_qualifications": "- Relevant experience in the field\n- Strong communication skills\n- Problem-solving ability",
            "preferred_qualifications": "- Advanced degree preferred\n- Industry certifications\n- Leadership experience",
            "benefits": "- Competitive salary\n- Health insurance\n- 401(k) matching\n- Flexible PTO\n- Remote work options",
        }

    try:
        import json
        from app.core.config import settings
        response = ai_brain.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert HR recruiter at a US-based company. Generate professional job postings. Respond ONLY with valid JSON, no markdown."
                },
                {
                    "role": "user",
                    "content": f"""Generate a complete job posting for:
Title: {title}
Department: {department or 'General'}

Return JSON:
{{
    "description": "2-3 paragraph overview of the role and company",
    "responsibilities": "8-10 bullet points, each starting with -",
    "required_qualifications": "6-8 bullet points, each starting with -",
    "preferred_qualifications": "4-5 bullet points, each starting with -",
    "benefits": "6-8 bullet points including health, 401k, PTO etc, each starting with -",
    "skills_required": ["skill1", "skill2", "skill3"],
    "experience_level": "entry|mid|senior|lead"
}}"""
                }
            ],
            max_tokens=1500,
            temperature=0.7,
        )
        text = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        result["title"] = title
        result["department"] = department
        return result
    except Exception as e:
        return {
            "title": title,
            "department": department,
            "description": f"We are seeking an experienced {title} to join our {department or 'team'}.",
            "responsibilities": "- Drive key initiatives\n- Collaborate across teams",
            "required_qualifications": "- Relevant experience\n- Strong skills",
            "preferred_qualifications": "- Advanced qualifications preferred",
            "benefits": "- Competitive salary and benefits package",
            "error": str(e),
        }


@router.post("/")
def create_job_posting(data: JobPostingCreate, db: Session = Depends(get_db)):
    logger.info(f"=== JOB CREATE === Data: {data.model_dump()}")
    job = JobPosting(**data.model_dump(exclude_none=True))
    db.add(job)

    log = ActivityLog(
        entity_type="job_posting",
        entity_id=0,
        action="created",
        description=f"Job posting created: {data.title}",
        actor="admin",
    )
    db.add(log)
    db.commit()
    db.refresh(job)

    log.entity_id = job.id
    db.commit()
    return job


@router.get("/")
def get_job_postings(status: str = None, db: Session = Depends(get_db)):
    query = db.query(JobPosting)
    if status:
        query = query.filter(JobPosting.status == status)
    return query.order_by(JobPosting.created_at.desc()).all()


@router.get("/{job_id}")
def get_job_posting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.put("/{job_id}")
def update_job_posting(job_id: int, data: JobPostingUpdate, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job_posting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    db.delete(job)
    db.commit()
    return {"message": "Job posting deleted"}
