import pytest

from backend.agents.template_generator import TemplateGenerator


class TestTemplateGenerator:
    @pytest.fixture
    def generator(self):
        return TemplateGenerator()

    def test_init(self, generator):
        assert generator is not None

    def test_generate_markdown_modern(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume, style="modern")
        assert md is not None
        assert "# 张三" in md
        assert "## 高级软件工程师" in md

    def test_generate_markdown_classic(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume, style="classic")
        assert md is not None
        assert "张三" in md

    def test_generate_markdown_minimalist(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume, style="minimalist")
        assert md is not None
        assert "# 王五" not in md  # 应该是张三
        assert "# 张三" in md

    def test_generate_markdown_default_style(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume)
        assert md is not None

    def test_generate_html(self, generator, sample_resume):
        html = generator.generate_html(sample_resume, style="modern")
        assert html is not None
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "张三" in html

    def test_generate_html_classic(self, generator, sample_resume):
        html = generator.generate_html(sample_resume, style="classic")
        assert html is not None
        assert "Times New Roman" in html or "serif" in html.lower()

    def test_generate_html_minimalist(self, generator, sample_resume):
        html = generator.generate_html(sample_resume, style="minimalist")
        assert html is not None

    def test_modern_template_contains_contact(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume, style="modern")
        assert "zhangsan@example.com" in md

    def test_modern_template_contains_skills(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume, style="modern")
        assert "技能" in md or "Skills" in md

    def test_modern_template_contains_experience(self, generator, sample_resume):
        md = generator.generate_markdown(sample_resume, style="modern")
        assert "工作经历" in md or "Experience" in md
