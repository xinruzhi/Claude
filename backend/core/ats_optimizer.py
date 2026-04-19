from typing import List, Set
from backend.models.resume import Resume


class ATSOptimizer:
    def __init__(self):
        self.common_keywords = {
            'software engineer': ['python', 'java', 'javascript', 'agile', 'scrum', 'api',
                                  'rest', 'git', 'docker', 'kubernetes', 'ci/cd', 'tdd',
                                  'microservices', 'aws', 'azure', 'sql', 'nosql'],
            'data scientist': ['python', 'machine learning', 'deep learning', 'tensorflow',
                               'pytorch', 'pandas', 'numpy', 'scikit-learn', 'sql',
                               'statistics', 'data visualization', 'nlp', 'computer vision'],
            'product manager': ['agile', 'scrum', 'user story', 'mvp', 'roadmap',
                                'stakeholder management', 'user research', 'a/b testing',
                                'kpi', 'okr', 'market research'],
            'ux designer': ['figma', 'user research', 'wireframing', 'prototyping',
                           'usability testing', 'design system', 'accessibility',
                           'information architecture', 'interaction design']
        }

    def optimize_for_ats(
        self,
        resume: Resume,
        target_role: str = None,
        keywords: List[str] = None
    ) -> Resume:
        optimized = resume.model_copy()

        target_keywords = self._get_target_keywords(target_role, keywords)
        missing_keywords = self._find_missing_keywords(resume, target_keywords)

        if missing_keywords:
            optimized = self._integrate_keywords(optimized, missing_keywords[:5])

        optimized = self._standardize_section_titles(optimized)
        optimized = self._ensure_proper_length(optimized)

        return optimized

    def calculate_ats_score(self, resume: Resume) -> float:
        score = 0.0
        total_checks = 10

        checks = [
            self._check_has_summary(resume),
            self._check_has_skills(resume),
            self._check_has_experience(resume),
            self._check_has_education(resume),
            self._check_experience_descriptions(resume),
            self._check_technical_skills(resume),
            self._check_action_verbs(resume),
            self._check_quantifiable_achievements(resume),
            self._check_contact_info(resume),
            self._check_proper_length(resume)
        ]

        return (sum(checks) / total_checks) * 100

    def _get_target_keywords(
        self,
        target_role: str = None,
        additional_keywords: List[str] = None
    ) -> Set[str]:
        keywords = set()

        if target_role:
            role_lower = target_role.lower()
            for role, role_keywords in self.common_keywords.items():
                if role in role_lower or role_lower in role:
                    keywords.update(role_keywords)

        if additional_keywords:
            keywords.update(k.lower() for k in additional_keywords)

        return keywords

    def _find_missing_keywords(self, resume: Resume, target_keywords: Set[str]) -> List[str]:
        resume_text = self._resume_to_text(resume).lower()
        missing = []

        for keyword in target_keywords:
            if keyword.lower() not in resume_text:
                missing.append(keyword)

        return missing

    def _integrate_keywords(self, resume: Resume, keywords: List[str]) -> Resume:
        optimized = resume.model_copy()

        if keywords:
            optimized.skills.extend([k for k in keywords if k not in optimized.skills])
            optimized.technical_skills.extend(
                [k for k in keywords if k not in optimized.technical_skills]
            )

        return optimized

    def _standardize_section_titles(self, resume: Resume) -> Resume:
        return resume

    def _ensure_proper_length(self, resume: Resume) -> Resume:
        return resume

    def _resume_to_text(self, resume: Resume) -> str:
        parts = [
            resume.name,
            resume.title,
            resume.summary,
            ' '.join(resume.skills),
            ' '.join(resume.technical_skills),
        ]

        for exp in resume.experience:
            parts.extend([
                exp.company,
                exp.position,
                ' '.join(exp.description),
                ' '.join(exp.achievements)
            ])

        for edu in resume.education:
            parts.extend([edu.school, edu.degree, edu.major])

        return ' '.join(parts)

    def _check_has_summary(self, resume: Resume) -> bool:
        return bool(resume.summary and len(resume.summary) >= 50)

    def _check_has_skills(self, resume: Resume) -> bool:
        return len(resume.skills) >= 5 or len(resume.technical_skills) >= 5

    def _check_has_experience(self, resume: Resume) -> bool:
        return len(resume.experience) >= 1

    def _check_has_education(self, resume: Resume) -> bool:
        return len(resume.education) >= 1

    def _check_experience_descriptions(self, resume: Resume) -> bool:
        return any(len(exp.description) >= 3 for exp in resume.experience)

    def _check_technical_skills(self, resume: Resume) -> bool:
        return len(resume.technical_skills) >= 3

    def _check_action_verbs(self, resume: Resume) -> bool:
        action_verbs = ['led', 'managed', 'developed', 'implemented', 'created',
                       'designed', 'improved', 'increased', 'reduced', 'built']
        text = self._resume_to_text(resume).lower()
        return any(verb in text for verb in action_verbs)

    def _check_quantifiable_achievements(self, resume: Resume) -> bool:
        text = self._resume_to_text(resume)
        import re
        return bool(re.search(r'\d+%|\d+\+|\$\d+', text))

    def _check_contact_info(self, resume: Resume) -> bool:
        return bool(resume.email)

    def _check_proper_length(self, resume: Resume) -> bool:
        text_length = len(self._resume_to_text(resume))
        return 500 <= text_length <= 5000
