from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from core.extractors import EXTRACTOR_REGISTRY


class TestExtractorRegistry:
    def test_all_types_registered(self):
        assert "invoice" in EXTRACTOR_REGISTRY
        assert "purchase_order" in EXTRACTOR_REGISTRY
        assert "contract" in EXTRACTOR_REGISTRY
        assert "resume" in EXTRACTOR_REGISTRY

    def test_extractor_document_types(self):
        for type_name, cls in EXTRACTOR_REGISTRY.items():
            extractor = cls()
            assert extractor.document_type == type_name
            assert hasattr(extractor, "extraction_prompt")
            assert hasattr(extractor, "validation_rules")

    def test_invoice_required_fields(self):
        extractor = EXTRACTOR_REGISTRY["invoice"]()
        rules = extractor.validation_rules
        assert rules["invoice_number"]["required"]
        assert rules["total"]["required"]

    def test_confidence_calculation(self):
        extractor = EXTRACTOR_REGISTRY["invoice"]()
        data = {"invoice_number": "INV-001", "total": 100.0}
        cleaned, confidence = extractor._post_process(data)
        assert 0 < confidence <= 1.0

    def test_empty_data_cleaning(self):
        extractor = EXTRACTOR_REGISTRY["invoice"]()
        data = {"invoice_number": "", "total": None, "vendor_name": []}
        cleaned, _ = extractor._post_process(data)
        assert "invoice_number" not in cleaned
        assert "total" not in cleaned
        assert "vendor_name" not in cleaned


class TestExtractorExtensibility:
    def test_new_type_can_be_registered(self):
        from core.extractors.base import BaseExtractor

        class TestExtractor(BaseExtractor):
            document_type = "test_doc"

            @property
            def extraction_prompt(self):
                return "Test prompt"

            @property
            def validation_rules(self):
                return {"field1": {"required": True, "type": "string"}}

        EXTRACTOR_REGISTRY["test_doc"] = TestExtractor
        assert "test_doc" in EXTRACTOR_REGISTRY
        del EXTRACTOR_REGISTRY["test_doc"]
