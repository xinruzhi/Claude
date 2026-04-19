import pytest
from unittest.mock import Mock, patch
from io import BytesIO

from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestRootEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestResumeEndpoints:
    @patch('api.routes.resume.ResumeParser')
    @patch('api.routes.resume.VersionManager')
    def test_upload_resume(self, mock_version_manager, mock_parser, client, sample_resume):
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = sample_resume
        mock_parser.return_value = mock_parser_instance

        mock_vm_instance = Mock()
        mock_vm_instance.save_version.return_value = "test1234"
        mock_version_manager.return_value = mock_vm_instance

        file_content = BytesIO(b"Test resume content")
        response = client.post(
            "/api/resume/upload",
            files={"file": ("resume.txt", file_content, "text/plain")},
            data={"name": "测试用户"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "resume_id" in data

    @patch('api.routes.resume.VersionManager')
    def test_get_resume(self, mock_version_manager, client, sample_resume):
        mock_vm_instance = Mock()
        mock_vm_instance.get_version.return_value = sample_resume
        mock_version_manager.return_value = mock_vm_instance

        response = client.get("/api/resume/test1234")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "张三"

    @patch('api.routes.resume.VersionManager')
    def test_get_resume_not_found(self, mock_version_manager, client):
        mock_vm_instance = Mock()
        mock_vm_instance.get_version.return_value = None
        mock_version_manager.return_value = mock_vm_instance

        response = client.get("/api/resume/nonexistent")
        assert response.status_code == 404

    @patch('api.routes.resume.VersionManager')
    def test_list_versions(self, mock_version_manager, client):
        mock_vm_instance = Mock()
        mock_vm_instance.list_versions.return_value = [
            {"version": "1.0", "version_note": "Initial", "saved_at": "2024-01-01"}
        ]
        mock_version_manager.return_value = mock_vm_instance

        response = client.get("/api/resume/test1234/versions")
        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert "versions" in data

    @patch('api.routes.resume.VersionManager')
    @patch('api.routes.resume.TemplateGenerator')
    def test_preview_resume(self, mock_template_gen, mock_version_manager, client, sample_resume):
        mock_vm_instance = Mock()
        mock_vm_instance.get_version.return_value = sample_resume
        mock_version_manager.return_value = mock_vm_instance

        mock_tg_instance = Mock()
        mock_tg_instance.generate_html.return_value = "<html>Test</html>"
        mock_template_gen.return_value = mock_tg_instance

        response = client.post(
            "/api/resume/test1234/preview",
            params={"style": "modern", "format": "html"}
        )
        assert response.status_code == 200


class TestOptimizeEndpoints:
    @patch('api.routes.optimize.VersionManager')
    @patch('api.routes.optimize.ContentOptimizer')
    def test_optimize_resume(self, mock_optimizer, mock_version_manager, client, sample_resume):
        mock_vm_instance = Mock()
        mock_vm_instance.get_version.return_value = sample_resume
        mock_vm_instance.save_version.return_value = "test1234"
        mock_version_manager.return_value = mock_vm_instance

        from backend.models.resume import ResumeOptimizationResult
        mock_opt_instance = Mock()
        mock_opt_instance.optimize_resume.return_value = ResumeOptimizationResult(
            original_resume=sample_resume,
            optimized_resume=sample_resume.model_copy(),
            suggestions=["建议1"],
            keywords_added=["Python"],
            ats_score=85.0,
            improvements=["改进1"]
        )
        mock_optimizer.return_value = mock_opt_instance

        response = client.post(
            "/api/optimize/test1234",
            data={
                "target_role": "软件工程师",
                "industry": "互联网"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ats_score" in data


class TestMatchEndpoints:
    @patch('api.routes.match.VersionManager')
    @patch('api.routes.match.JobMatcher')
    def test_match_resume(self, mock_matcher, mock_version_manager, client, sample_resume):
        mock_vm_instance = Mock()
        mock_vm_instance.get_version.return_value = sample_resume
        mock_version_manager.return_value = mock_vm_instance

        from backend.models.job_description import MatchResult, JobDescription
        job_desc = JobDescription(
            title="测试职位",
            company="测试公司",
            description="测试描述"
        )
        mock_matcher_instance = Mock()
        mock_matcher_instance.match_resume_to_job.return_value = MatchResult(
            job_description=job_desc,
            match_score=75.5,
            skill_match_score=80.0,
            experience_match_score=70.0,
            keyword_match_score=75.0,
            matched_skills=["Python"],
            missing_skills=[],
            matched_keywords=[],
            missing_keywords=[],
            suggestions=[],
            improvements=[]
        )
        mock_matcher.return_value = mock_matcher_instance

        response = client.post(
            "/api/match/test1234",
            data={
                "job_title": "高级Python工程师",
                "company": "测试公司",
                "job_description": "这是职位描述"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "match_score" in data
