from __future__ import annotations

from core.extractors.base import BaseExtractor


class ContractExtractor(BaseExtractor):
    document_type = "contract"

    @property
    def extraction_prompt(self) -> str:
        return (
            "You are a contract data extraction specialist. Extract the following fields from this contract document. "
            "Return a JSON object with these fields:\n"
            "- contract_title (string)\n"
            "- parties (array of objects with: name, role)\n"
            "- effective_date (string in YYYY-MM-DD format)\n"
            "- expiration_date (string in YYYY-MM-DD format)\n"
            "- contract_value (number)\n"
            "- governing_law (string)\n"
            "- jurisdiction (string)\n"
            "- key_terms (array of strings - important clauses, obligations, rights)\n"
            "- termination_clause (string - summary of termination conditions)\n"
            "- renewal_terms (string - description of renewal conditions)\n"
            "Extract all fields accurately. If a field is not present, set it to null. "
            "For parties, extract all named parties and their roles in the contract."
        )

    @property
    def validation_rules(self) -> dict:
        return {
            "parties": {"required": True, "type": "array"},
            "effective_date": {"required": True, "type": "date"},
            "contract_title": {"required": False, "type": "string"},
        }

    @property
    def confidence_boosters(self) -> list[str]:
        return ["key_terms", "governing_law", "contract_value", "expiration_date"]
