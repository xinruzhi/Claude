from typing import List, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from backend.models.resume import Resume, ResumeOptimizationResult
from config.settings import get_settings

settings = get_settings()


class ContentOptimizer:
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.llm = ChatAnthropic(
            model=model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7
        )

    def optimize_resume(
        self,
        resume: Resume,
        target_role: Optional[str] = None,
        industry: Optional[str] = None
    ) -> ResumeOptimizationResult:
        system_prompt = self._build_system_prompt(target_role, industry)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请优化以下简历：\n\n{resume.model_dump_json(indent=2)}")
        ])

        chain = prompt | self.llm

        response = chain.invoke({})

        optimized_resume = self._parse_optimized_resume(response.content, resume)
        suggestions = self._extract_suggestions(response.content)
        keywords_added = self._extract_keywords_added(response.content)
        improvements = self._extract_improvements(response.content)

        ats_score = self._calculate_ats_score(optimized_resume)

        return ResumeOptimizationResult(
            original_resume=resume,
            optimized_resume=optimized_resume,
            suggestions=suggestions,
            keywords_added=keywords_added,
            ats_score=ats_score,
            improvements=improvements
        )

    def _build_system_prompt(self, target_role: Optional[str], industry: Optional[str]) -> str:
        base = """你是一位专业的简历优化专家，拥有10年以上的HR和招聘经验。你的任务是：

1. 优化简历内容，使其更具说服力
2. 使用量化的成就描述
3. 添加行业相关关键词，提高ATS通过率
4. 优化语言表达，使其更专业
5. 确保简历结构清晰易读

请提供：
1. 优化后的完整简历
2. 具体的改进建议
3. 添加的关键词列表
4. 改进点的详细说明

请用JSON格式返回结果。"""

        if target_role:
            base += f"\n\n目标职位：{target_role}"
        if industry:
            base += f"\n行业：{industry}"

        return base

    def _parse_optimized_resume(self, response: str, original: Resume) -> Resume:
        optimized = original.model_copy()

        if "summary" in response.lower():
            lines = response.split('\n')
            for i, line in enumerate(lines):
                if "summary" in line.lower() and i + 1 < len(lines):
                    optimized.summary = lines[i + 1].strip()
                    break

        return optimized

    def _extract_suggestions(self, response: str) -> List[str]:
        suggestions = []
        lines = response.split('\n')
        in_suggestions = False

        for line in lines:
            if "建议" in line or "suggestion" in line.lower():
                in_suggestions = True
                continue
            if in_suggestions and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                    suggestions.append(line.strip().lstrip('1234567890.-* '))
                elif line.strip():
                    suggestions.append(line.strip())
            elif in_suggestions and not line.strip():
                break

        return suggestions[:10]

    def _extract_keywords_added(self, response: str) -> List[str]:
        keywords = []
        lines = response.split('\n')
        in_keywords = False

        for line in lines:
            if "关键词" in line or "keyword" in line.lower():
                in_keywords = True
                continue
            if in_keywords and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                    keywords.append(line.strip().lstrip('1234567890.-* '))
                elif ',' in line:
                    keywords.extend([k.strip() for k in line.split(',') if k.strip()])
                elif line.strip():
                    keywords.append(line.strip())
            elif in_keywords and not line.strip():
                break

        return keywords

    def _extract_improvements(self, response: str) -> List[str]:
        improvements = []
        lines = response.split('\n')
        in_improvements = False

        for line in lines:
            if "改进" in line or "improvement" in line.lower():
                in_improvements = True
                continue
            if in_improvements and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                    improvements.append(line.strip().lstrip('1234567890.-* '))
                elif line.strip():
                    improvements.append(line.strip())
            elif in_improvements and not line.strip():
                break

        return improvements[:10]

    def _calculate_ats_score(self, resume: Resume) -> float:
        score = 50.0

        if resume.summary and len(resume.summary) > 100:
            score += 10
        if len(resume.skills) >= 10:
            score += 10
        if len(resume.experience) >= 2:
            score += 10
        if any(len(exp.description) >= 3 for exp in resume.experience):
            score += 10
        if len(resume.technical_skills) >= 5:
            score += 10

        return min(score, 100.0)
