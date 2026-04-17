from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.employee import Employee
from app.models.interview import Interview
from app.models.job_posting import JobPosting
from app.models.activity_log import ActivityLog
from app.models.ai_action import AIAction

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get all dashboard statistics"""
    total_candidates = db.query(Candidate).count()
    active_candidates = db.query(Candidate).filter(
        Candidate.status.notin_(["rejected", "hired"])
    ).count()
    total_employees = db.query(Employee).filter(Employee.status == "active").count()
    interviews_scheduled = db.query(Interview).filter(Interview.result == "pending").count()
    active_jobs = db.query(JobPosting).filter(JobPosting.status == "active").count()
    ai_actions = db.query(AIAction).count()

    # Pipeline breakdown
    pipeline = {}
    stages = ["applied", "screening", "technical", "hr", "offer", "hired", "rejected"]
    for stage in stages:
        pipeline[stage] = db.query(Candidate).filter(Candidate.status == stage).count()

    return {
        "total_candidates": total_candidates,
        "active_candidates": active_candidates,
        "total_employees": total_employees,
        "interviews_scheduled": interviews_scheduled,
        "active_jobs": active_jobs,
        "ai_actions": ai_actions,
        "pipeline": pipeline,
    }


@router.get("/pipeline")
def get_pipeline_data(db: Session = Depends(get_db)):
    """Get candidates grouped by pipeline stage"""
    stages = ["applied", "screening", "technical", "hr", "offer", "hired", "rejected"]
    result = {}
    for stage in stages:
        candidates = db.query(Candidate).filter(Candidate.status == stage).all()
        result[stage] = [
            {
                "id": c.id,
                "name": c.name or c.email.split("@")[0],
                "email": c.email,
                "job_role": c.job_role,
                "ai_score": c.ai_score,
                "applied_at": str(c.applied_at) if c.applied_at else None,
            }
            for c in candidates
        ]
    return result


@router.get("/activity")
def get_recent_activity(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent activity logs"""
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
    return logs


@router.get("/hiring-funnel")
def get_hiring_funnel(db: Session = Depends(get_db)):
    """Get hiring funnel metrics"""
    total = db.query(Candidate).count()
    screened = db.query(Candidate).filter(Candidate.status.notin_(["applied"])).count()
    interviewed = db.query(Candidate).filter(
        Candidate.status.in_(["technical", "hr", "offer", "hired"])
    ).count()
    offered = db.query(Candidate).filter(Candidate.status.in_(["offer", "hired"])).count()
    hired = db.query(Candidate).filter(Candidate.status == "hired").count()

    return {
        "funnel": [
            {"stage": "Applied", "count": total},
            {"stage": "Screened", "count": screened},
            {"stage": "Interviewed", "count": interviewed},
            {"stage": "Offered", "count": offered},
            {"stage": "Hired", "count": hired},
        ]
    }
