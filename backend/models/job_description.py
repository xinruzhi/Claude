from pydantic import BaseModel, Field
from typing import List, Optional


class JobRequirement(BaseModel):
    skill: str = Field(..., description="技能要求")
    required: bool = Field(True, description="是否必需")
    priority: int = Field(1, description="优先级，1-5")


class JobDescription(BaseModel):
    id: Optional[str] = Field(None, description="职位描述ID")
    title: str = Field(..., description="职位名称")
    company: str = Field(..., description="公司名称")
    location: Optional[str] = Field(None, description="位置")
    description: str = Field(..., description="职位描述全文")

    requirements: List[JobRequirement] = Field(default_factory=list, description="要求列表")
    responsibilities: List[str] = Field(default_factory=list, description="职责列表")
    benefits: List[str] = Field(default_factory=list, description="福利列表")

    keywords: List[str] = Field(default_factory=list, description="关键词")
    technical_keywords: List[str] = Field(default_factory=list, description="技术关键词")
    soft_keywords: List[str] = Field(default_factory=list, description="软技能关键词")

    salary_range: Optional[str] = Field(None, description="薪资范围")
    employment_type: Optional[str] = Field(None, description="雇佣类型")
    seniority_level: Optional[str] = Field(None, description="职级")


class MatchResult(BaseModel):
    job_description: JobDescription
    match_score: float = Field(..., description="匹配分数 0-100")
    skill_match_score: float = Field(..., description="技能匹配分数")
    experience_match_score: float = Field(..., description="经验匹配分数")
    keyword_match_score: float = Field(..., description="关键词匹配分数")

    matched_skills: List[str] = Field(default_factory=list, description="匹配的技能")
    missing_skills: List[str] = Field(default_factory=list, description="缺失的技能")
    matched_keywords: List[str] = Field(default_factory=list, description="匹配的关键词")
    missing_keywords: List[str] = Field(default_factory=list, description="缺失的关键词")

    suggestions: List[str] = Field(default_factory=list, description="改进建议")
    improvements: List[str] = Field(default_factory=list, description="具体改进点")
