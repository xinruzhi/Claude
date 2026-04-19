import os
from typing import Optional
from pathlib import Path
import PyPDF2
from docx import Document
import markdown

from backend.models.resume import Resume, Experience, Education, Project


class ResumeParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> Optional[Resume]:
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext == '.docx':
            return self._parse_docx(file_path)
        elif ext in ['.md', '.markdown']:
            return self._parse_markdown(file_path)
        elif ext in ['.txt']:
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _parse_pdf(self, file_path: str) -> Optional[Resume]:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return self._parse_text_content(text)

    def _parse_docx(self, file_path: str) -> Optional[Resume]:
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        return self._parse_text_content(text)

    def _parse_markdown(self, file_path: str) -> Optional[Resume]:
        with open(file_path, 'r') as f:
            text = f.read()
        return self._parse_text_content(text)

    def _parse_text(self, file_path: str) -> Optional[Resume]:
        with open(file_path, 'r') as f:
            text = f.read()
        return self._parse_text_content(text)

    def _parse_text_content(self, text: str) -> Optional[Resume]:
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        resume = Resume(
            name="",
            title="",
            email="",
            summary=""
        )

        current_section = None
        current_experience: Optional[Experience] = None

        for i, line in enumerate(lines):
            line_lower = line.lower()

            if '@' in line and '.' in line and not resume.email:
                resume.email = line.strip()
                if not resume.name:
                    resume.name = lines[i-1] if i > 0 else "Unknown"
                continue

            section_headers = {
                'summary': ['summary', 'about', 'profile', 'objective'],
                'experience': ['experience', 'work experience', 'employment history'],
                'education': ['education', 'academic background'],
                'skills': ['skills', 'technical skills', 'core competencies'],
                'projects': ['projects', 'side projects'],
                'certifications': ['certifications', 'certificates'],
            }

            for section, keywords in section_headers.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section
                    break
            else:
                if current_section == 'summary' and not resume.summary:
                    resume.summary = line
                elif current_section == 'skills':
                    resume.skills.append(line)
                elif current_section == 'experience':
                    if not current_experience or any(keyword in line_lower for keyword in ['company', 'inc', 'llc', 'co']):
                        if current_experience:
                            resume.experience.append(current_experience)
                        current_experience = Experience(
                            company=line,
                            position="",
                            start_date="",
                            description=[]
                        )
                    elif current_experience:
                        if not current_experience.position:
                            current_experience.position = line
                        else:
                            current_experience.description.append(line)

        if current_experience:
            resume.experience.append(current_experience)

        return resume
