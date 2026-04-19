import pytest
import json
from pathlib import Path

from backend.core.version_manager import VersionManager
from backend.models.resume import Resume


class TestVersionManager:
    def test_init_creates_storage_dir(self, temp_dir):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        assert (temp_dir / "resumes").exists()

    def test_save_new_resume(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume, "Test version")

        assert resume_id is not None
        assert len(resume_id) == 8

        resume_dir = temp_dir / "resumes" / resume_id
        assert resume_dir.exists()
        assert (resume_dir / "latest.json").exists()
        assert (resume_dir / "1.0.json").exists()

    def test_save_resume_with_id(self, temp_dir, sample_resume):
        sample_resume.id = "test1234"
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume)

        assert resume_id == "test1234"

    def test_get_latest_version(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume)

        retrieved = manager.get_version(resume_id, "latest")
        assert retrieved is not None
        assert retrieved.name == sample_resume.name

    def test_get_specific_version(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume)

        retrieved = manager.get_version(resume_id, "1.0")
        assert retrieved is not None
        assert retrieved.version == "1.0"

    def test_get_nonexistent_resume(self, temp_dir):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        retrieved = manager.get_version("nonexistent")
        assert retrieved is None

    def test_list_versions(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume, "First version")

        versions = manager.list_versions(resume_id)
        assert len(versions) == 1
        assert versions[0]["version"] == "1.0"
        assert versions[0]["version_note"] == "First version"

    def test_create_new_version(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume, "Initial")

        new_resume = manager.create_new_version(
            resume_id,
            {"title": "更新的职位"},
            "Updated title"
        )

        assert new_resume is not None
        assert new_resume.version == "1.1"
        assert new_resume.title == "更新的职位"

        versions = manager.list_versions(resume_id)
        assert len(versions) == 2

    def test_delete_resume(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume)

        resume_dir = temp_dir / "resumes" / resume_id
        assert resume_dir.exists()

        result = manager.delete_resume(resume_id)
        assert result is True
        assert not resume_dir.exists()

    def test_delete_nonexistent_resume(self, temp_dir):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        result = manager.delete_resume("nonexistent")
        assert result is False

    def test_version_note_saved(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume, "This is a test note")

        resume_dir = temp_dir / "resumes" / resume_id
        version_file = resume_dir / "1.0.json"

        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data["version_note"] == "This is a test note"

    def test_resume_timestamps(self, temp_dir, sample_resume):
        manager = VersionManager(storage_dir=str(temp_dir / "resumes"))
        resume_id = manager.save_version(sample_resume)

        retrieved = manager.get_version(resume_id)
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
