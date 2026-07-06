from __future__ import annotations

from typing import Optional

from app.core.config import settings


class ConfidenceAnalyzer:
    def analyze(self, extraction: dict, validation: list[dict], historical_patterns: list[dict]) -> dict:
        base_confidence = extraction.get("confidence_score", 0.0)
        
        # Apply pattern boosts
        pattern_boost = 0.0
        for pattern in historical_patterns:
            if pattern.get("field_name") == extraction.get("field_name"):
                pattern_boost = pattern.get("confidence_boost", 0.0)
                break
        
        # Validation penalties
        validation_penalty = 0.0
        for v in validation:
            if v.get("status") == "error":
                validation_penalty += 0.15
            elif v.get("status") == "warning":
                validation_penalty += 0.05
        
        adjusted = base_confidence + pattern_boost - validation_penalty
        adjusted = max(0.0, min(1.0, adjusted))
        
        needs_review = adjusted < settings.confidence_threshold_auto
        needs_mcq = adjusted < settings.confidence_threshold_mcq
        
        return {
            "base_confidence": base_confidence,
            "pattern_boost": pattern_boost,
            "validation_penalty": validation_penalty,
            "adjusted_confidence": round(adjusted, 2),
            "needs_review": needs_review,
            "needs_mcq": needs_mcq,
            "auto_approve": adjusted >= settings.confidence_threshold_auto,
        }
