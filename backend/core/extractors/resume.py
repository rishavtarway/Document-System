from __future__ import annotations

from core.extractors.base import BaseExtractor


class ResumeExtractor(BaseExtractor):
    document_type = "resume"

    @property
    def extraction_prompt(self) -> str:
        return (
            "You are a resume data extraction specialist. Extract the following fields from this resume document. "
            "Return a JSON object with these fields:\n"
            "- candidate_name (string, required)\n"
            "- email (string)\n"
            "- phone (string)\n"
            "- address (string)\n"
            "- skills (array of strings)\n"
            "- experience (array of objects with: company, role, start_date, end_date, responsibilities[strings])\n"
            "- education (array of objects with: institution, degree, field, start_year, end_year)\n"
            "- certifications (array of strings)\n"
            "- summary (string - professional summary or objective)\n"
            "Extract all fields accurately. If a field is not present, set it to null. "
            "List all skills, work experiences (most recent first), and educational qualifications."
        )

    @property
    def validation_rules(self) -> dict:
        return {
            "candidate_name": {"required": True, "type": "string"},
            "skills": {"required": False, "type": "array"},
            "experience": {"required": False, "type": "array"},
            "education": {"required": False, "type": "array"},
        }

    @property
    def confidence_boosters(self) -> list[str]:
        return ["email", "phone", "skills", "experience", "education"]
