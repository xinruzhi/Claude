from fastapi import APIRouter, HTTPException, Form
from typing import Optional

from backend.models.resume import Resume
from backend.models.job_description import JobDescription
from backend.core.version_manager import VersionManager
from backend.agents.job_matcher import JobMatcher

router = APIRouter()
version_manager = VersionManager()
matcher = JobMatcher()


@router.post("/{resume_id}")
async def match_resume(
    resume_id: str,
    job_title: str = Form(...),
    company: str = Form(...),
    job_description: str = Form(...),
    location: Optional[str] = Form(None)
):
    resume = version_manager.get_version(resume_id, "latest")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = JobDescription(
        title=job_title,
        company=company,
        description=job_description,
        location=location
    )

    try:
        result = matcher.match_resume_to_job(resume, job)
        return {
            "success": True,
            "match_score": result.match_score,
            "skill_match_score": result.skill_match_score,
            "experience_match_score": result.experience_match_score,
            "keyword_match_score": result.keyword_match_score,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills,
            "matched_keywords": result.matched_keywords,
            "missing_keywords": result.missing_keywords,
            "suggestions": result.suggestions,
            "improvements": result.improvements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/direct")
async def match_direct(resume: Resume, job: JobDescription):
    try:
        result = matcher.match_resume_to_job(resume, job)
        return {
            "success": True,
            "match_score": result.match_score,
            "skill_match_score": result.skill_match_score,
            "experience_match_score": result.experience_match_score,
            "keyword_match_score": result.keyword_match_score,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills,
            "matched_keywords": result.matched_keywords,
            "missing_keywords": result.missing_keywords,
            "suggestions": result.suggestions,
            "improvements": result.improvements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
