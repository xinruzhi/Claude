import pytest

from backend.core.ats_optimizer import ATSOptimizer
from backend.models.resume import Resume


class TestATSOptimizer:
    @pytest.fixture
    def optimizer(self):
        return ATSOptimizer()

    def test_init(self, optimizer):
        assert optimizer is not None
        assert isinstance(optimizer.common_keywords, dict)

    def test_get_target_keywords_by_role(self, optimizer):
        keywords = optimizer._get_target_keywords(target_role="software engineer")
        assert len(keywords) > 0
        assert "python" in keywords
        assert "git" in keywords

    def test_get_target_keywords_additional(self, optimizer):
        keywords = optimizer._get_target_keywords(
            additional_keywords=["custom1", "custom2"]
        )
        assert "custom1" in keywords
        assert "custom2" in keywords

    def test_find_missing_keywords(self, optimizer, sample_resume):
        target_keywords = {"python", "java", "javascript", "nonexistent"}
        missing = optimizer._find_missing_keywords(sample_resume, target_keywords)
        assert len(missing) > 0

    def test_calculate_ats_score(self, optimizer, sample_resume):
        score = optimizer.calculate_ats_score(sample_resume)
        assert 0 <= score <= 100

    def test_calculate_ats_score_minimal(self, optimizer, minimal_resume):
        score = optimizer.calculate_ats_score(minimal_resume)
        assert 0 <= score <= 100

    def test_check_has_summary(self, optimizer, sample_resume, minimal_resume):
        assert optimizer._check_has_summary(sample_resume) is True
        assert optimizer._check_has_summary(minimal_resume) is True

    def test_check_has_skills(self, optimizer, sample_resume, minimal_resume):
        assert optimizer._check_has_skills(sample_resume) is True
        assert optimizer._check_has_skills(minimal_resume) is False

    def test_check_has_experience(self, optimizer, sample_resume, minimal_resume):
        assert optimizer._check_has_experience(sample_resume) is True
        assert optimizer._check_has_experience(minimal_resume) is False

    def test_check_has_education(self, optimizer, sample_resume, minimal_resume):
        assert optimizer._check_has_education(sample_resume) is True
        assert optimizer._check_has_education(minimal_resume) is False

    def test_check_contact_info(self, optimizer, sample_resume, minimal_resume):
        assert optimizer._check_contact_info(sample_resume) is True
        assert optimizer._check_contact_info(minimal_resume) is True

    def test_check_action_verbs(self, optimizer):
        resume = Resume(
            name="Test",
            title="Test",
            email="test@test.com",
            summary="Led a team and managed projects. Developed new features."
        )
        assert optimizer._check_action_verbs(resume) is True

    def test_check_quantifiable_achievements(self, optimizer):
        resume = Resume(
            name="Test",
            title="Test",
            email="test@test.com",
            summary="Increased sales by 50% and reduced costs by 30%."
        )
        assert optimizer._check_quantifiable_achievements(resume) is True

    def test_resume_to_text(self, optimizer, sample_resume):
        text = optimizer._resume_to_text(sample_resume)
        assert "张三" in text
        assert "高级软件工程师" in text
        assert "Python" in text

    def test_optimize_for_ats(self, optimizer, sample_resume):
        optimized = optimizer.optimize_for_ats(
            sample_resume,
            target_role="software engineer"
        )
        assert optimized is not None
        assert optimized.name == sample_resume.name
