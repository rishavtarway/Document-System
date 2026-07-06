from __future__ import annotations

import re
from datetime import datetime
from typing import Optional


class FieldValidator:
    @staticmethod
    def validate_email(value: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))
    
    @staticmethod
    def validate_phone(value: str) -> bool:
        cleaned = re.sub(r"[\s\-\(\)\.]", "", value)
        return bool(re.match(r"^\+?\d{7,15}$", cleaned))
    
    @staticmethod
    def validate_date(value: str) -> bool:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%B %d, %Y", "%d-%m-%Y"):
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False
    
    @staticmethod
    def validate_tax_id(value: str) -> bool:
        return bool(re.match(r"^\d{2}-\d{7}$|^\d{9}$|^[A-Z0-9]{6,15}$", value))
    
    @staticmethod
    def validate_number(value) -> bool:
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def normalize_date(value: str) -> Optional[str]:
        for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%B %d, %Y", "%d-%m-%Y", "%m-%d-%Y"):
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None


class ValidationService:
    def __init__(self):
        self.field_validator = FieldValidator()
    
    def validate_extraction(self, document_type: str, extracted_data: list[dict], schema: dict) -> list[dict]:
        results = []
        fields = schema.get("fields", [])
        fields_map = {f["name"]: f for f in fields}
        
        for extraction in extracted_data:
            field_name = extraction.get("field_name", "")
            field_def = fields_map.get(field_name, {})
            value = extraction.get("extracted_value", "")
            field_type = field_def.get("type", "string")
            
            validation = self._validate_field(field_name, value, field_type, field_def)
            extraction["validation"] = validation
            results.append(validation)
        
        # Cross-field validations
        cross = self._cross_field_validation(extracted_data, document_type)
        results.extend(cross)
        
        return results
    
    def _validate_field(self, field_name: str, value: str, field_type: str, field_def: dict) -> dict:
        result = {"field": field_name, "status": "passed", "message": None, "suggested_value": None}
        
        if field_def.get("required") and (not value or value == "null" or value == ""):
            result["status"] = "error"
            result["message"] = f"Required field '{field_name}' is missing"
            return result
        
        if not value or value == "null":
            result["status"] = "warning"
            result["message"] = f"Field '{field_name}' is empty"
            return result
        
        if field_type == "date":
            if not self.field_validator.validate_date(value):
                suggested = self.field_validator.normalize_date(value)
                result["status"] = "warning"
                result["message"] = f"Date '{value}' has unrecognized format"
                result["suggested_value"] = suggested
        
        elif field_type == "number":
            if not self.field_validator.validate_number(value):
                result["status"] = "error"
                result["message"] = f"'{value}' is not a valid number"
            elif float(value) < 0:
                result["status"] = "warning"
                result["message"] = f"Negative value '{value}' may be incorrect"
        
        elif "email" in field_name.lower():
            if not self.field_validator.validate_email(value):
                result["status"] = "warning"
                result["message"] = f"'{value}' may not be a valid email"
        
        elif "phone" in field_name.lower():
            if not self.field_validator.validate_phone(value):
                result["status"] = "warning"
                result["message"] = f"'{value}' may not be a valid phone number"
        
        elif field_type == "tax_id":
            if not self.field_validator.validate_tax_id(value):
                result["status"] = "warning"
                result["message"] = f"'{value}' may not be a valid tax ID"
        
        return result
    
    def _cross_field_validation(self, extracted_data: list[dict], document_type: str) -> list[dict]:
        results = []
        data = {e["field_name"]: e.get("extracted_value") for e in extracted_data}
        
        if "subtotal" in data and "total" in data and "invoice" in document_type:
            try:
                subtotal = float(data["subtotal"]) if data["subtotal"] else 0
                total = float(data["total"]) if data["total"] else 0
                if subtotal > 0 and total > 0 and total < subtotal * 0.5:
                    results.append({
                        "field": "total",
                        "status": "warning",
                        "message": "Total is significantly less than subtotal, verify",
                    })
            except (ValueError, TypeError):
                pass
        
        return results
