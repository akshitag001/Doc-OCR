"""Custom exceptions for Document OCR service."""


class DocumentQualityError(Exception):
    """Raised when document quality is too low to extract meaningful text."""
    pass


class UnsupportedDocumentError(Exception):
    """Raised when document format is not supported."""
    pass
