from core.extractors.base import BaseExtractor
from core.extractors.invoice import InvoiceExtractor
from core.extractors.purchase_order import PurchaseOrderExtractor
from core.extractors.contract import ContractExtractor
from core.extractors.resume import ResumeExtractor

EXTRACTOR_REGISTRY: dict[str, type[BaseExtractor]] = {
    "invoice": InvoiceExtractor,
    "purchase_order": PurchaseOrderExtractor,
    "contract": ContractExtractor,
    "resume": ResumeExtractor,
}

__all__ = [
    "BaseExtractor",
    "InvoiceExtractor",
    "PurchaseOrderExtractor",
    "ContractExtractor",
    "ResumeExtractor",
    "EXTRACTOR_REGISTRY",
]
