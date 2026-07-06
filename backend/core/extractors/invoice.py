from __future__ import annotations

from core.extractors.base import BaseExtractor


class InvoiceExtractor(BaseExtractor):
    document_type = "invoice"

    @property
    def extraction_prompt(self) -> str:
        return (
            "You are an invoice data extraction specialist. Extract the following fields from this invoice document. "
            "Return a JSON object with these fields:\n"
            "- invoice_number (string, required)\n"
            "- date (string in YYYY-MM-DD format)\n"
            "- due_date (string in YYYY-MM-DD format)\n"
            "- vendor_name (string)\n"
            "- vendor_address (string)\n"
            "- customer_name (string)\n"
            "- customer_address (string)\n"
            "- line_items (array of objects with: description, quantity, unit_price, total, sku)\n"
            "- subtotal (number)\n"
            "- tax (number)\n"
            "- total (number, required)\n"
            "- currency (string, default 'USD')\n"
            "- payment_terms (string)\n"
            "Extract all fields accurately. If a field is not present, set it to null. "
            "Normalize amounts to numeric values. For line_items, extract every line item listed."
        )

    @property
    def validation_rules(self) -> dict:
        return {
            "invoice_number": {"required": True, "type": "string"},
            "total": {"required": True, "type": "number"},
            "vendor_name": {"required": True, "type": "string"},
            "date": {"required": False, "type": "date"},
            "due_date": {"required": False, "type": "date"},
            "currency": {"required": False, "type": "string"},
        }

    @property
    def confidence_boosters(self) -> list[str]:
        return ["line_items", "subtotal", "tax", "customer_name"]
