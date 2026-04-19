from fastapi import APIRouter, HTTPException, Form
from typing import Optional

from backend.models.resume import Resume
from backend.core.version_manager import VersionManager
from backend.agents.content_optimizer import ContentOptimizer

router = APIRouter()
version_manager = VersionManager()
optimizer = ContentOptimizer()


@router.post("/{resume_id}")
async def optimize_resume(
    resume_id: str,
    target_role: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    version_note: str = "Optimized version"
):
    resume = version_manager.get_version(resume_id, "latest")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        result = optimizer.optimize_resume(resume, target_role, industry)

        new_version = version_manager.save_version(
            result.optimized_resume,
            version_note
        )

        return {
            "success": True,
            "resume_id": new_version,
            "original_resume": result.original_resume.model_dump(exclude_none=True),
            "optimized_resume": result.optimized_resume.model_dump(exclude_none=True),
            "suggestions": result.suggestions,
            "keywords_added": result.keywords_added,
            "ats_score": result.ats_score,
            "improvements": result.improvements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content")
async def optimize_content_direct(resume: Resume):
    try:
        result = optimizer.optimize_resume(resume)
        return {
            "success": True,
            "optimized_resume": result.optimized_resume.model_dump(exclude_none=True),
            "suggestions": result.suggestions,
            "keywords_added": result.keywords_added,
            "ats_score": result.ats_score,
            "improvements": result.improvements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
