from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Experience(BaseModel):
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位")
    start_date: str = Field(..., description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    description: List[str] = Field(default_factory=list, description="工作描述")
    achievements: List[str] = Field(default_factory=list, description="成就")


class Education(BaseModel):
    school: str = Field(..., description="学校名称")
    degree: str = Field(..., description="学位")
    major: str = Field(..., description="专业")
    start_date: str = Field(..., description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    gpa: Optional[str] = Field(None, description="GPA")


class Project(BaseModel):
    name: str = Field(..., description="项目名称")
    description: str = Field(..., description="项目描述")
    technologies: List[str] = Field(default_factory=list, description="使用的技术")
    link: Optional[str] = Field(None, description="项目链接")


class Resume(BaseModel):
    id: Optional[str] = Field(None, description="简历ID")
    version: str = Field("1.0", description="版本号")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    name: str = Field(..., description="姓名")
    title: str = Field(..., description="职位标题")
    email: str = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    location: Optional[str] = Field(None, description="位置")
    linkedin: Optional[str] = Field(None, description="LinkedIn链接")
    website: Optional[str] = Field(None, description="个人网站")

    summary: str = Field(..., description="个人简介")

    skills: List[str] = Field(default_factory=list, description="技能列表")
    technical_skills: List[str] = Field(default_factory=list, description="技术技能")
    soft_skills: List[str] = Field(default_factory=list, description="软技能")

    experience: List[Experience] = Field(default_factory=list, description="工作经历")
    education: List[Education] = Field(default_factory=list, description="教育背景")
    projects: List[Project] = Field(default_factory=list, description="项目经历")

    certifications: List[str] = Field(default_factory=list, description="证书")
    languages: List[str] = Field(default_factory=list, description="语言")

    template_style: str = Field("modern", description="模板风格")


class ResumeOptimizationResult(BaseModel):
    original_resume: Resume
    optimized_resume: Resume
    suggestions: List[str]
    keywords_added: List[str]
    ats_score: float
    improvements: List[str]
