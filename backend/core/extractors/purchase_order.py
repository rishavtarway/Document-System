from __future__ import annotations

from core.extractors.base import BaseExtractor


class PurchaseOrderExtractor(BaseExtractor):
    document_type = "purchase_order"

    @property
    def extraction_prompt(self) -> str:
        return (
            "You are a purchase order data extraction specialist. Extract the following fields from this PO document. "
            "Return a JSON object with these fields:\n"
            "- po_number (string, required)\n"
            "- date (string in YYYY-MM-DD format)\n"
            "- vendor_name (string, required)\n"
            "- vendor_address (string)\n"
            "- ship_to_address (string)\n"
            "- bill_to_address (string)\n"
            "- items (array of objects with: description, quantity, unit_price, total, sku)\n"
            "- total (number)\n"
            "- delivery_date (string in YYYY-MM-DD format)\n"
            "- payment_terms (string)\n"
            "- requisitioner (string)\n"
            "Extract all fields accurately. If a field is not present, set it to null. "
            "For items, extract every line item listed with its quantities and prices."
        )

    @property
    def validation_rules(self) -> dict:
        return {
            "po_number": {"required": True, "type": "string"},
            "vendor_name": {"required": True, "type": "string"},
            "date": {"required": False, "type": "date"},
            "total": {"required": False, "type": "number"},
        }

    @property
    def confidence_boosters(self) -> list[str]:
        return ["items", "ship_to_address", "bill_to_address", "requisitioner"]
