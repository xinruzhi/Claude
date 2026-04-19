import tempfile
from pathlib import Path
from typing import Optional

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from backend.models.resume import Resume
from backend.agents.template_generator import TemplateGenerator


class PDFGenerator:
    def __init__(self):
        self.template_generator = TemplateGenerator()

    def generate_pdf(
        self,
        resume: Resume,
        output_path: Optional[str] = None,
        style: str = "modern"
    ) -> str:
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("weasyprint is not installed. Install it with: pip install weasyprint")

        html_content = self.template_generator.generate_html(resume, style)

        if output_path is None:
            output_path = f"./outputs/{resume.name.replace(' ', '_')}_resume.pdf"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        HTML(string=html_content).write_pdf(output_path)

        return output_path

    def generate_pdf_from_html(
        self,
        html_content: str,
        output_path: str
    ) -> str:
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("weasyprint is not installed. Install it with: pip install weasyprint")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html_content).write_pdf(output_path)

        return output_path
