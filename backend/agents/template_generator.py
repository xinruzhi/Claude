from typing import Dict, Any
from pathlib import Path
import markdown

from backend.models.resume import Resume


class TemplateGenerator:
    def __init__(self, templates_dir: str = "backend/templates"):
        self.templates_dir = Path(templates_dir)

    def generate_markdown(self, resume: Resume, style: str = "modern") -> str:
        template = self._get_template(style)
        return template.format(resume=resume)

    def generate_html(self, resume: Resume, style: str = "modern") -> str:
        md_content = self.generate_markdown(resume, style)
        html_content = markdown.markdown(md_content, extensions=['extra'])

        html_template = self._get_html_template(style)
        return html_template.format(
            title=f"{resume.name} - {resume.title}",
            content=html_content,
            resume=resume
        )

    def _get_template(self, style: str) -> str:
        templates = {
            "modern": self._modern_template(),
            "classic": self._classic_template(),
            "minimalist": self._minimalist_template()
        }
        return templates.get(style, templates["modern"])

    def _modern_template(self) -> str:
        return """# {resume.name}

## {resume.title}

📧 {resume.email} | 📍 {resume.location or 'Location'} | 💼 {resume.linkedin or 'LinkedIn'}

---

## 个人简介

{resume.summary}

---

## 技能

{skills_section}

---

## 工作经历

{experience_section}

---

## 教育背景

{education_section}

---

## 项目经历

{projects_section}

---

## 其他

{certifications_section}
{languages_section}
"""

    def _classic_template(self) -> str:
        return """{resume.name}
{resume.title}

联系方式
Email: {resume.email}
电话: {resume.phone or 'N/A'}
地址: {resume.location or 'N/A'}

================================================================================

个人简介
{resume.summary}

================================================================================

专业技能
{skills_section}

================================================================================

工作经历
{experience_section}

================================================================================

教育背景
{education_section}

================================================================================

项目经历
{projects_section}
"""

    def _minimalist_template(self) -> str:
        return """# {resume.name}

{resume.title}

{resume.email}

---

{resume.summary}

---

## Skills
{skills_section}

---

## Experience
{experience_section}

---

## Education
{education_section}
"""

    def _get_html_template(self, style: str) -> str:
        styles = {
            "modern": """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 20px;
        line-height: 1.6;
        color: #333;
    }
    h1 { color: #2563eb; font-size: 2.5em; margin-bottom: 0.2em; }
    h2 { color: #1e40af; border-bottom: 2px solid #2563eb; padding-bottom: 0.3em; }
    .contact { color: #6b7280; margin-bottom: 2em; }
    hr { border: none; border-top: 1px solid #e5e7eb; margin: 2em 0; }
</style>
""",
            "classic": """
<style>
    body {
        font-family: 'Times New Roman', serif;
        max-width: 8.5in;
        margin: 1in auto;
        line-height: 1.4;
        color: #000;
    }
    h1 { font-size: 24pt; text-align: center; margin-bottom: 5pt; }
    h2 { font-size: 14pt; margin-top: 20pt; margin-bottom: 10pt; border-bottom: 1px solid #000; }
</style>
""",
            "minimalist": """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        max-width: 700px;
        margin: 0 auto;
        padding: 60px 30px;
        line-height: 1.7;
        color: #111;
    }
    h1 { font-weight: 300; font-size: 2.5em; margin-bottom: 0.1em; }
    h2 { font-weight: 500; font-size: 1.1em; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 2em; }
</style>
"""
        }
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    {styles.get(style, styles['modern'])}
</head>
<body>
{{content}}
</body>
</html>"""
