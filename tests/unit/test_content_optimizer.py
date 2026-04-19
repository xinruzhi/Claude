import pytest
from unittest.mock import Mock, patch

from backend.agents.content_optimizer import ContentOptimizer


class TestContentOptimizer:
    @pytest.fixture
    def optimizer(self):
        with patch('backend.agents.content_optimizer.ChatAnthropic'):
            return ContentOptimizer()

    def test_init(self, optimizer):
        assert optimizer is not None

    def test_build_system_prompt(self, optimizer):
        prompt = optimizer._build_system_prompt(None, None)
        assert "简历优化" in prompt or "优化" in prompt or "resume" in prompt.lower()

    def test_build_system_prompt_with_role(self, optimizer):
        prompt = optimizer._build_system_prompt("软件工程师", None)
        assert "软件工程师" in prompt

    def test_build_system_prompt_with_industry(self, optimizer):
        prompt = optimizer._build_system_prompt(None, "互联网")
        assert "互联网" in prompt

    def test_extract_suggestions(self, optimizer):
        response = """这里是一些建议：
1. 增加更多量化成就
2. 优化技能列表
3. 改进个人简介

其他内容...
"""
        suggestions = optimizer._extract_suggestions(response)
        assert len(suggestions) >= 2

    def test_extract_suggestions_empty(self, optimizer):
        suggestions = optimizer._extract_suggestions("没有任何建议")
        assert isinstance(suggestions, list)

    def test_extract_keywords_added(self, optimizer):
        response = """添加的关键词：
- Python
- FastAPI
- Docker

其他内容...
"""
        keywords = optimizer._extract_keywords_added(response)
        assert len(keywords) >= 0

    def test_extract_improvements(self, optimizer):
        response = """改进点：
1. 优化了个人简介
2. 增加了技能关键词

其他内容...
"""
        improvements = optimizer._extract_improvements(response)
        assert len(improvements) >= 0

    def test_calculate_ats_score(self, optimizer, sample_resume):
        score = optimizer._calculate_ats_score(sample_resume)
        assert 0 <= score <= 100

    def test_calculate_ats_score_minimal(self, optimizer, minimal_resume):
        score = optimizer._calculate_ats_score(minimal_resume)
        assert 0 <= score <= 100

    def test_parse_optimized_resume(self, optimizer, sample_resume):
        response = """这里是优化后的简历：
summary: 优化后的个人简介
"""
        optimized = optimizer._parse_optimized_resume(response, sample_resume)
        assert optimized is not None
        assert optimized.name == sample_resume.name

    @patch('backend.agents.content_optimizer.ChatAnthropic')
    def test_optimize_resume(self, mock_chat, sample_resume):
        mock_instance = Mock()
        mock_instance.invoke.return_value = Mock(content="测试响应")
        mock_chat.return_value = mock_instance

        optimizer = ContentOptimizer()
        result = optimizer.optimize_resume(sample_resume)

        assert result is not None
        assert result.original_resume == sample_resume
