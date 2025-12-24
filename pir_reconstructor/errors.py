class ReconstructionError(Exception):
    """Base exception for reconstruction errors."""
    pass

class ValidationError(ReconstructionError):
    """Raised when PIR validation fails."""
    pass

class ParserError(ReconstructionError):
    """Raised when PIR parsing fails."""
    pass

class LayerError(ReconstructionError):
    """Raised when a reconstruction layer fails."""
    pass
