from __future__ import annotations

import pytest


class TestDocumentClassifier:
    def test_pattern_based_invoice(self):
        from app.services.document_classifier import DocumentClassifier
        classifier = DocumentClassifier()
        
        text = "INVOICE NUMBER: INV-2024-001\nBill To: Acme Corp\nSubtotal: $1,000.00"
        result = classifier._pattern_based_classification(text)
        
        assert result["document_type"] == "invoice"
        assert result["confidence"] > 0.5
    
    def test_pattern_based_resume(self):
        from app.services.document_classifier import DocumentClassifier
        classifier = DocumentClassifier()
        
        text = "RESUME\nJohn Doe\nEXPERIENCE: Software Engineer at Tech Co\nEDUCATION: MIT"
        result = classifier._pattern_based_classification(text)
        
        assert result["document_type"] == "resume"
    
    def test_pattern_based_unknown(self):
        from app.services.document_classifier import DocumentClassifier
        classifier = DocumentClassifier()
        
        text = "This is a random piece of text without any document indicators"
        result = classifier._pattern_based_classification(text)
        
        assert result["document_type"] == "unknown"
        assert result["confidence"] == 0.0


class TestGibberishDetection:
    def test_normal_text(self):
        from app.services.extractor_service import IntelligentExtractor
        extractor = IntelligentExtractor()
        
        assert not extractor._is_gibberish("Hello World")
        assert not extractor._is_gibberish("INV-001 $1,234.56")
    
    def test_gibberish_text(self):
        from app.services.extractor_service import IntelligentExtractor
        extractor = IntelligentExtractor()
        
        assert extractor._is_gibberish("")
        assert extractor._is_gibberish("a")
        assert extractor._is_gibberish("!@#$%^&*()_+")


class TestFieldValidator:
    def test_email_validation(self):
        from app.services.validation_service import FieldValidator
        v = FieldValidator()
        
        assert v.validate_email("user@example.com")
        assert v.validate_email("a.b@c.co")
        assert not v.validate_email("not-an-email")
        assert not v.validate_email("")
    
    def test_phone_validation(self):
        from app.services.validation_service import FieldValidator
        v = FieldValidator()
        
        assert v.validate_phone("+1234567890")
        assert v.validate_phone("(555) 123-4567")
        assert not v.validate_phone("abc")
    
    def test_date_validation(self):
        from app.services.validation_service import FieldValidator
        v = FieldValidator()
        
        assert v.validate_date("2024-01-15")
        assert v.validate_date("01/15/2024")
        assert not v.validate_date("not-a-date")
    
    def test_date_normalization(self):
        from app.services.validation_service import FieldValidator
        v = FieldValidator()
        
        assert v.normalize_date("01/15/2024") == "2024-01-15"
        assert v.normalize_date("2024/01/15") == "2024-01-15"
        assert v.normalize_date("invalid") is None


class TestConfidenceAnalyzer:
    def test_confidence_adjustment(self):
        from app.services.confidence_analyzer import ConfidenceAnalyzer
        analyzer = ConfidenceAnalyzer()
        
        extraction = {"field_name": "total", "confidence_score": 0.8}
        validation = [{"field": "total", "status": "passed"}]
        
        result = analyzer.analyze(extraction, validation, [])
        
        assert result["adjusted_confidence"] == 0.8
        assert result["needs_review"] is False
    
    def test_confidence_validation_penalty(self):
        from app.services.confidence_analyzer import ConfidenceAnalyzer
        analyzer = ConfidenceAnalyzer()
        
        extraction = {"field_name": "total", "confidence_score": 0.9}
        validation = [{"field": "total", "status": "error"}]
        
        result = analyzer.analyze(extraction, validation, [])
        
        assert result["adjusted_confidence"] < 0.9
        assert result["validation_penalty"] == 0.15
