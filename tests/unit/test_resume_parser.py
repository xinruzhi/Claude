import pytest
from pathlib import Path

from backend.core.resume_parser import ResumeParser


class TestResumeParser:
    @pytest.fixture
    def parser(self):
        return ResumeParser()

    def test_init(self, parser):
        assert parser is not None

    def test_parse_text_content(self, parser):
        text = """张三
高级软件工程师

zhangsan@example.com

Summary
拥有5年软件开发经验的全栈工程师。

Skills
Python
JavaScript
Git

Experience
ABC科技有限公司
软件工程师
负责后端开发和维护
"""
        resume = parser._parse_text_content(text)
        assert resume is not None

    def test_parse_text_finds_email(self, parser):
        text = "测试姓名\ntest@example.com"
        resume = parser._parse_text_content(text)
        assert resume.email == "test@example.com"

    def test_parse_markdown_file(self, parser, temp_dir, sample_markdown_resume):
        md_file = temp_dir / "resume.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(sample_markdown_resume)

        resume = parser.parse_file(str(md_file))
        assert resume is not None

    def test_parse_text_file(self, parser, temp_dir):
        text_file = temp_dir / "resume.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("Test Name\ntest@example.com\n")

        resume = parser.parse_file(str(text_file))
        assert resume is not None

    def test_unsupported_file_format(self, parser, temp_dir):
        unknown_file = temp_dir / "resume.xyz"
        unknown_file.touch()

        with pytest.raises(ValueError):
            parser.parse_file(str(unknown_file))

    def test_nonexistent_file(self, parser):
        with pytest.raises(Exception):
            parser.parse_file("nonexistent_file.pdf")
