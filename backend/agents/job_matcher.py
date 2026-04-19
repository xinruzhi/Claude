from typing import List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from backend.models.resume import Resume
from backend.models.job_description import JobDescription, MatchResult
from config.settings import get_settings

settings = get_settings()


class JobMatcher:
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.llm = ChatAnthropic(
            model=model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7
        )

    def match_resume_to_job(
        self,
        resume: Resume,
        job_description: JobDescription
    ) -> MatchResult:
        system_prompt = self._build_system_prompt()

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
请分析以下简历与职位描述的匹配度：

【简历】
{resume.model_dump_json(indent=2)}

【职位描述】
{job_description.model_dump_json(indent=2)}

请提供：
1. 总体匹配分数 (0-100)
2. 技能匹配分数
3. 经验匹配分数
4. 关键词匹配分数
5. 匹配的技能列表
6. 缺失的技能列表
7. 匹配的关键词列表
8. 缺失的关键词列表
9. 改进建议
10. 具体改进点
""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({})

        return self._parse_match_result(response.content, resume, job_description)

    def _build_system_prompt(self) -> str:
        return """你是一位专业的招聘专家，拥有10年以上的技术招聘经验。你的任务是：

1. 客观分析简历与职位描述的匹配度
2. 识别候选人的优势与不足
3. 提供具体、可操作的改进建议
4. 分析技能匹配情况
5. 识别关键词的匹配情况

请用清晰的结构返回分析结果，使用JSON格式或清晰的列表格式。

评分标准：
- 90-100分：高度匹配，完全符合要求
- 75-89分：良好匹配，基本符合要求
- 60-74分：一般匹配，需要一些改进
- 40-59分：较低匹配，需要较多改进
- 0-39分：不匹配"""

    def _parse_match_result(
        self,
        response: str,
        resume: Resume,
        job_description: JobDescription
    ) -> MatchResult:
        match_score = self._extract_score(response, "总体匹配")
        skill_match_score = self._extract_score(response, "技能匹配")
        experience_match_score = self._extract_score(response, "经验匹配")
        keyword_match_score = self._extract_score(response, "关键词匹配")

        matched_skills = self._extract_list(response, "匹配的技能")
        missing_skills = self._extract_list(response, "缺失的技能")
        matched_keywords = self._extract_list(response, "匹配的关键词")
        missing_keywords = self._extract_list(response, "缺失的关键词")
        suggestions = self._extract_list(response, "改进建议")
        improvements = self._extract_list(response, "具体改进点")

        if not matched_skills:
            matched_skills = self._find_matched_skills(resume, job_description)
        if not missing_skills:
            missing_skills = self._find_missing_skills(resume, job_description)

        return MatchResult(
            job_description=job_description,
            match_score=match_score,
            skill_match_score=skill_match_score,
            experience_match_score=experience_match_score,
            keyword_match_score=keyword_match_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            suggestions=suggestions,
            improvements=improvements
        )

    def _extract_score(self, response: str, keyword: str) -> float:
        lines = response.split('\n')
        for line in lines:
            if keyword in line:
                import re
                match = re.search(r'(\d+(?:\.\d+)?)', line)
                if match:
                    return float(match.group(1))
        return 50.0

    def _extract_list(self, response: str, keyword: str) -> List[str]:
        items = []
        lines = response.split('\n')
        in_list = False

        for line in lines:
            if keyword in line:
                in_list = True
                continue
            if in_list and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                    items.append(line.strip().lstrip('1234567890.-* '))
                elif line.strip():
                    items.append(line.strip())
            elif in_list and not line.strip() and items:
                break

        return items

    def _find_matched_skills(self, resume: Resume, job: JobDescription) -> List[str]:
        resume_skills = set(s.lower() for s in resume.skills + resume.technical_skills)
        matched = []
        for req in job.requirements:
            if req.skill.lower() in resume_skills:
                matched.append(req.skill)
        return matched

    def _find_missing_skills(self, resume: Resume, job: JobDescription) -> List[str]:
        resume_skills = set(s.lower() for s in resume.skills + resume.technical_skills)
        missing = []
        for req in job.requirements:
            if req.skill.lower() not in resume_skills:
                missing.append(req.skill)
        return missing
