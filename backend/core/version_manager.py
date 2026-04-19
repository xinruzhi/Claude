import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil

from backend.models.resume import Resume


class VersionManager:
    def __init__(self, storage_dir: str = "./data/resumes"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_version(self, resume: Resume, version_note: str = "") -> str:
        if not resume.id:
            resume.id = self._generate_id()

        resume.updated_at = datetime.now()
        if not resume.created_at:
            resume.created_at = resume.updated_at

        resume_dir = self.storage_dir / resume.id
        resume_dir.mkdir(exist_ok=True)

        version_file = resume_dir / f"{resume.version}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            data = resume.model_dump()
            data['version_note'] = version_note
            data['saved_at'] = datetime.now().isoformat()
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        latest_file = resume_dir / "latest.json"
        shutil.copy(version_file, latest_file)

        return resume.id

    def get_version(self, resume_id: str, version: str = "latest") -> Optional[Resume]:
        resume_dir = self.storage_dir / resume_id
        if not resume_dir.exists():
            return None

        version_file = resume_dir / f"{version}.json"
        if not version_file.exists():
            return None

        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data.pop('version_note', None)
            data.pop('saved_at', None)
            return Resume(**data)

    def list_versions(self, resume_id: str) -> List[Dict]:
        resume_dir = self.storage_dir / resume_id
        if not resume_dir.exists():
            return []

        versions = []
        for file in resume_dir.glob("*.json"):
            if file.stem == "latest":
                continue
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                versions.append({
                    'version': file.stem,
                    'version_note': data.get('version_note', ''),
                    'saved_at': data.get('saved_at', ''),
                    'updated_at': data.get('updated_at', '')
                })

        return sorted(versions, key=lambda x: x['saved_at'], reverse=True)

    def create_new_version(self, resume_id: str, changes: Dict, version_note: str = "") -> Optional[Resume]:
        latest = self.get_version(resume_id, "latest")
        if not latest:
            return None

        version_parts = latest.version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        new_version = '.'.join(version_parts)

        new_resume = latest.model_copy(update=changes)
        new_resume.version = new_version

        self.save_version(new_resume, version_note)
        return new_resume

    def delete_resume(self, resume_id: str) -> bool:
        resume_dir = self.storage_dir / resume_id
        if resume_dir.exists():
            shutil.rmtree(resume_dir)
            return True
        return False

    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())[:8]
