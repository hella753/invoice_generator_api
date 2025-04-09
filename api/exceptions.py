

class InvoiceGenerationError(Exception):
    """
    Exception raised when invoice generation fails.
    """
    pass


class LanguageNotSupportedError(Exception):
    """
    Exception raised when the requested language is not supported.
    """
    pass
