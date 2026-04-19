from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import uuid
from typing import Optional

from backend.models.resume import Resume
from backend.core.resume_parser import ResumeParser
from backend.core.version_manager import VersionManager
from backend.agents.template_generator import TemplateGenerator
from backend.utils.pdf_generator import PDFGenerator
from config.settings import get_settings

router = APIRouter()
settings = get_settings()

parser = ResumeParser()
version_manager = VersionManager()
template_generator = TemplateGenerator()
pdf_generator = PDFGenerator()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None)
):
    file_id = str(uuid.uuid4())[:8]
    file_ext = Path(file.filename).suffix
    file_path = Path(settings.upload_dir) / f"{file_id}{file_ext}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resume = parser.parse_file(str(file_path))
        if resume and name:
            resume.name = name

        if resume:
            resume_id = version_manager.save_version(resume, "Initial upload")
            return {
                "success": True,
                "resume_id": resume_id,
                "resume": resume.model_dump(exclude_none=True)
            }
        else:
            return {
                "success": False,
                "error": "Could not parse resume"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{resume_id}")
async def get_resume(resume_id: str, version: str = "latest"):
    resume = version_manager.get_version(resume_id, version)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume.model_dump(exclude_none=True)


@router.get("/{resume_id}/versions")
async def list_versions(resume_id: str):
    versions = version_manager.list_versions(resume_id)
    return {"resume_id": resume_id, "versions": versions}


@router.post("/{resume_id}/preview")
async def preview_resume(
    resume_id: str,
    style: str = "modern",
    format: str = "html"
):
    resume = version_manager.get_version(resume_id, "latest")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if format == "html":
        html = template_generator.generate_html(resume, style)
        return {"html": html}
    elif format == "markdown":
        md = template_generator.generate_markdown(resume, style)
        return {"markdown": md}
    else:
        raise HTTPException(status_code=400, detail="Invalid format")


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    style: str = "modern",
    format: str = "pdf"
):
    resume = version_manager.get_version(resume_id, "latest")
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    output_dir = Path(settings.output_dir)
    output_dir.mkdir(exist_ok=True)

    if format == "pdf":
        output_path = output_dir / f"{resume_id}_{style}.pdf"
        pdf_generator.generate_pdf(resume, str(output_path), style)
        return FileResponse(
            str(output_path),
            media_type="application/pdf",
            filename=f"{resume.name.replace(' ', '_')}_resume.pdf"
        )
    elif format == "markdown":
        output_path = output_dir / f"{resume_id}_{style}.md"
        md = template_generator.generate_markdown(resume, style)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        return FileResponse(
            str(output_path),
            media_type="text/markdown",
            filename=f"{resume.name.replace(' ', '_')}_resume.md"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format")
