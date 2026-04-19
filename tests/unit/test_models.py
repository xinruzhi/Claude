import pytest
from datetime import datetime

from backend.models.resume import (
    Resume,
    Experience,
    Education,
    Project,
    ResumeOptimizationResult
)
from backend.models.job_description import (
    JobDescription,
    JobRequirement,
    MatchResult
)


class TestExperience:
    def test_create_experience(self):
        exp = Experience(
            company="Test Company",
            position="Developer",
            start_date="2020-01",
            description=["Worked on projects"]
        )
        assert exp.company == "Test Company"
        assert exp.position == "Developer"
        assert exp.start_date == "2020-01"
        assert exp.end_date is None
        assert len(exp.description) == 1
        assert len(exp.achievements) == 0

    def test_experience_with_end_date(self):
        exp = Experience(
            company="Test Company",
            position="Developer",
            start_date="2020-01",
            end_date="2023-01",
            description=["Worked"],
            achievements=["Achieved goal"]
        )
        assert exp.end_date == "2023-01"
        assert len(exp.achievements) == 1


class TestEducation:
    def test_create_education(self):
        edu = Education(
            school="Test University",
            degree="Bachelor",
            major="Computer Science",
            start_date="2015-09"
        )
        assert edu.school == "Test University"
        assert edu.degree == "Bachelor"
        assert edu.major == "Computer Science"
        assert edu.gpa is None

    def test_education_with_gpa(self):
        edu = Education(
            school="Test University",
            degree="Master",
            major="Data Science",
            start_date="2018-09",
            end_date="2021-06",
            gpa="3.9/4.0"
        )
        assert edu.gpa == "3.9/4.0"
        assert edu.end_date == "2021-06"


class TestProject:
    def test_create_project(self):
        proj = Project(
            name="Test Project",
            description="A test project",
            technologies=["Python", "FastAPI"]
        )
        assert proj.name == "Test Project"
        assert proj.description == "A test project"
        assert len(proj.technologies) == 2
        assert proj.link is None


class TestResume:
    def test_create_resume(self, sample_resume):
        assert sample_resume.name == "张三"
        assert sample_resume.title == "高级软件工程师"
        assert sample_resume.email == "zhangsan@example.com"
        assert len(sample_resume.skills) == 4
        assert len(sample_resume.technical_skills) == 4
        assert len(sample_resume.experience) == 1
        assert len(sample_resume.education) == 1
        assert len(sample_resume.projects) == 1

    def test_resume_defaults(self, minimal_resume):
        assert minimal_resume.version == "1.0"
        assert minimal_resume.template_style == "modern"
        assert minimal_resume.skills == []
        assert minimal_resume.experience == []
        assert minimal_resume.education == []

    def test_resume_with_created_at(self, sample_resume):
        assert sample_resume.created_at is not None
        assert isinstance(sample_resume.created_at, datetime)

    def test_resume_model_dump(self, sample_resume):
        data = sample_resume.model_dump(exclude_none=True)
        assert "name" in data
        assert "title" in data
        assert "email" in data
        assert "skills" in data

    def test_resume_copy(self, sample_resume):
        copied = sample_resume.model_copy()
        assert copied.name == sample_resume.name
        assert copied.id == sample_resume.id
        copied.name = "新名字"
        assert sample_resume.name == "张三"


class TestResumeOptimizationResult:
    def test_create_optimization_result(self, sample_resume):
        optimized = sample_resume.model_copy()
        optimized.summary = "优化后的简介"

        result = ResumeOptimizationResult(
            original_resume=sample_resume,
            optimized_resume=optimized,
            suggestions=["建议1", "建议2"],
            keywords_added=["Python", "FastAPI"],
            ats_score=85.5,
            improvements=["改进1"]
        )

        assert result.original_resume.name == "张三"
        assert result.optimized_resume.summary == "优化后的简介"
        assert len(result.suggestions) == 2
        assert len(result.keywords_added) == 2
        assert result.ats_score == 85.5


class TestJobRequirement:
    def test_create_job_requirement(self):
        req = JobRequirement(
            skill="Python",
            required=True,
            priority=5
        )
        assert req.skill == "Python"
        assert req.required is True
        assert req.priority == 5

    def test_job_requirement_defaults(self):
        req = JobRequirement(skill="JavaScript")
        assert req.required is True
        assert req.priority == 1


class TestJobDescription:
    def test_create_job_description(self, sample_job_description):
        assert sample_job_description.title == "高级Python工程师"
        assert sample_job_description.company == "XYZ互联网公司"
        assert len(sample_job_description.requirements) == 5
        assert len(sample_job_description.responsibilities) == 3
        assert len(sample_job_description.keywords) == 5

    def test_job_description_defaults(self):
        job = JobDescription(
            title="测试职位",
            company="测试公司",
            description="测试描述"
        )
        assert job.requirements == []
        assert job.responsibilities == []
        assert job.keywords == []


class TestMatchResult:
    def test_create_match_result(self, sample_resume, sample_job_description):
        result = MatchResult(
            job_description=sample_job_description,
            match_score=75.5,
            skill_match_score=80.0,
            experience_match_score=70.0,
            keyword_match_score=75.0,
            matched_skills=["Python", "FastAPI"],
            missing_skills=["AWS"],
            matched_keywords=["Python", "FastAPI"],
            missing_keywords=["微服务"],
            suggestions=["添加AWS相关经验"],
            improvements=["提升技能匹配度"]
        )

        assert result.job_description.title == "高级Python工程师"
        assert result.match_score == 75.5
        assert result.skill_match_score == 80.0
        assert len(result.matched_skills) == 2
        assert len(result.missing_skills) == 1
        assert len(result.suggestions) == 1
