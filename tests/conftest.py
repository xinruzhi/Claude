import pytest
import tempfile
import shutil
from pathlib import Path

from backend.models.resume import Resume, Experience, Education, Project
from backend.models.job_description import JobDescription, JobRequirement


@pytest.fixture
def sample_resume():
    return Resume(
        name="张三",
        title="高级软件工程师",
        email="zhangsan@example.com",
        phone="13800138000",
        location="北京",
        linkedin="https://linkedin.com/in/zhangsan",
        summary="拥有5年软件开发经验的全栈工程师，专注于Python和Web开发。",
        skills=["Python", "JavaScript", "Git", "Docker"],
        technical_skills=["FastAPI", "React", "PostgreSQL", "Redis"],
        soft_skills=["团队协作", "问题解决", "沟通能力"],
        experience=[
            Experience(
                company="ABC科技有限公司",
                position="软件工程师",
                start_date="2020-01",
                end_date="2023-01",
                description=[
                    "负责后端API开发和维护",
                    "参与系统架构设计"
                ],
                achievements=["优化系统性能30%", "带领3人团队完成项目"]
            )
        ],
        education=[
            Education(
                school="北京大学",
                degree="硕士",
                major="计算机科学与技术",
                start_date="2015-09",
                end_date="2018-06",
                gpa="3.8/4.0"
            )
        ],
        projects=[
            Project(
                name="电商平台",
                description="一个完整的电商解决方案",
                technologies=["Python", "FastAPI", "React"],
                link="https://github.com/zhangsan/ecommerce"
            )
        ],
        certifications=["AWS Certified Developer", "PMP"],
        languages=["中文", "英语"],
        template_style="modern"
    )


@pytest.fixture
def minimal_resume():
    return Resume(
        name="李四",
        title="初级开发工程师",
        email="lisi@example.com",
        summary="刚毕业的计算机专业学生，热爱编程。"
    )


@pytest.fixture
def sample_job_description():
    return JobDescription(
        title="高级Python工程师",
        company="XYZ互联网公司",
        location="上海",
        description="我们正在寻找一位经验丰富的Python工程师加入我们的团队。",
        requirements=[
            JobRequirement(skill="Python", required=True, priority=5),
            JobRequirement(skill="FastAPI", required=True, priority=4),
            JobRequirement(skill="PostgreSQL", required=True, priority=4),
            JobRequirement(skill="Docker", required=False, priority=3),
            JobRequirement(skill="AWS", required=False, priority=2)
        ],
        responsibilities=[
            "负责后端服务开发",
            "参与技术选型和架构设计",
            "指导初级工程师"
        ],
        keywords=["Python", "FastAPI", "PostgreSQL", "微服务", "REST API"],
        technical_keywords=["Python", "FastAPI", "PostgreSQL", "Docker"],
        soft_keywords=["团队协作", "沟通能力", "问题解决"],
        salary_range="30K-50K",
        employment_type="全职",
        seniority_level="高级"
    )


@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    yield Path(dir_path)
    shutil.rmtree(dir_path)


@pytest.fixture
def sample_markdown_resume():
    return """# 王五

## 软件工程师

📧 wangwu@example.com | 📍 深圳

---

## 个人简介

拥有3年Python开发经验，熟悉Web开发和数据分析。

---

## 技能

- Python
- Django
- MySQL
- Git

---

## 工作经历

### DEF公司
软件工程师 | 2021-01 至 2023-12

- 负责Web应用开发
- 维护数据库
"""
