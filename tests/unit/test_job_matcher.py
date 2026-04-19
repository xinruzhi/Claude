import pytest
from unittest.mock import Mock, patch

from backend.agents.job_matcher import JobMatcher


class TestJobMatcher:
    @pytest.fixture
    def matcher(self):
        with patch('backend.agents.job_matcher.ChatAnthropic'):
            return JobMatcher()

    def test_init(self, matcher):
        assert matcher is not None

    def test_build_system_prompt(self, matcher):
        prompt = matcher._build_system_prompt()
        assert "招聘" in prompt or "匹配" in prompt or "match" in prompt.lower()

    def test_extract_score(self, matcher):
        score = matcher._extract_score("总体匹配分数：75.5分", "总体匹配")
        assert score == 75.5

    def test_extract_score_integer(self, matcher):
        score = matcher._extract_score("技能匹配：80", "技能匹配")
        assert score == 80.0

    def test_extract_score_not_found(self, matcher):
        score = matcher._extract_score("没有分数", "不存在")
        assert score == 50.0

    def test_extract_list(self, matcher):
        response = """匹配的技能：
- Python
- FastAPI
- Git

其他内容...
"""
        items = matcher._extract_list(response, "匹配的技能")
        assert isinstance(items, list)

    def test_extract_list_empty(self, matcher):
        items = matcher._extract_list("没有列表内容", "不存在")
        assert isinstance(items, list)

    def test_find_matched_skills(self, matcher, sample_resume, sample_job_description):
        matched = matcher._find_matched_skills(sample_resume, sample_job_description)
        assert isinstance(matched, list)

    def test_find_missing_skills(self, matcher, sample_resume, sample_job_description):
        missing = matcher._find_missing_skills(sample_resume, sample_job_description)
        assert isinstance(missing, list)

    def test_parse_match_result(self, matcher, sample_resume, sample_job_description):
        response = """总体匹配：75
技能匹配：80
经验匹配：70
关键词匹配：75
"""
        result = matcher._parse_match_result(response, sample_resume, sample_job_description)

        assert result is not None
        assert result.job_description == sample_job_description
        assert 0 <= result.match_score <= 100

    @patch('backend.agents.job_matcher.ChatAnthropic')
    def test_match_resume_to_job(self, mock_chat, sample_resume, sample_job_description):
        mock_instance = Mock()
        mock_instance.invoke.return_value = Mock(content="测试响应")
        mock_chat.return_value = mock_instance

        matcher = JobMatcher()
        result = matcher.match_resume_to_job(sample_resume, sample_job_description)

        assert result is not None
        assert result.job_description == sample_job_description
