from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from core.extractors import EXTRACTOR_REGISTRY, BaseExtractor
from core.schemas import ValidationResult


class FieldValidator:
    @staticmethod
    def validate_date(value: str) -> bool:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False

    @staticmethod
    def validate_email(value: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))

    @staticmethod
    def validate_phone(value: str) -> bool:
        cleaned = re.sub(r"[\s\-\(\)\.]", "", value)
        return bool(re.match(r"^\+?\d{7,15}$", cleaned))

    @staticmethod
    def validate_number(value) -> bool:
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False


def validate_extraction(
    document_type: str, extracted_data: dict
) -> list[ValidationResult]:
    extractor_cls = EXTRACTOR_REGISTRY.get(document_type)
    if not extractor_cls:
        return []

    extractor: BaseExtractor = extractor_cls()
    rules = extractor.validation_rules
    results: list[ValidationResult] = []

    for field, rule in rules.items():
        value = extracted_data.get(field)
        field_type = rule.get("type", "string")

        if rule.get("required") and (value is None or value == ""):
            results.append(
                ValidationResult(
                    field=field,
                    status="error",
                    message=f"Required field '{field}' is missing",
                )
            )
            continue

        if value is None or value == "":
            continue

        if field_type == "date" and isinstance(value, str):
            if not FieldValidator.validate_date(value):
                results.append(
                    ValidationResult(
                        field=field,
                        status="warning",
                        message=f"Date '{value}' has unrecognized format",
                        suggested_value=_normalize_date(value),
                    )
                )

        if field_type == "number":
            if not FieldValidator.validate_number(value):
                results.append(
                    ValidationResult(
                        field=field,
                        status="error",
                        message=f"'{value}' is not a valid number",
                    )
                )
            elif isinstance(value, (int, float)) and value < 0:
                results.append(
                    ValidationResult(
                        field=field,
                        status="warning",
                        message=f"Negative value '{value}' may be incorrect",
                    )
                )

        if "email" in field.lower() and isinstance(value, str):
            if not FieldValidator.validate_email(value):
                results.append(
                    ValidationResult(
                        field=field,
                        status="warning",
                        message=f"'{value}' may not be a valid email",
                    )
                )

        if "phone" in field.lower() and isinstance(value, str):
            if not FieldValidator.validate_phone(value):
                results.append(
                    ValidationResult(
                        field=field,
                        status="warning",
                        message=f"'{value}' may not be a valid phone number",
                    )
                )

    # Cross-field validations
    if "subtotal" in extracted_data and "total" in extracted_data:
        subtotal = extracted_data.get("subtotal")
        total = extracted_data.get("total")
        try:
            if subtotal and total and float(subtotal) > float(total) * 1.5:
                results.append(
                    ValidationResult(
                        field="total",
                        status="warning",
                        message="Total is significantly less than subtotal, may be incorrect",
                    )
                )
        except (ValueError, TypeError):
            pass

    return results


def _normalize_date(value: str) -> Optional[str]:
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%B %d, %Y", "%d-%m-%Y", "%m-%d-%Y"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None
