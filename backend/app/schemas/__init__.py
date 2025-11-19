"""
Pydantic schemas for API request/response models.
"""

from .common import (
    GrammarPoint,
    Vocabulary,
    TBCLLevel,
    ArticleType,
    QuestionType,
)

from .generate import (
    GenerateArticleRequest,
    GenerateArticleResponse,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    Question,
)

from .validate import (
    ValidateRequest,
    ValidateResponse,
    GrammarCheckResult,
    VocabCheckResult,
)

from .export import (
    ExportRequest,
    ExportResponse,
    ExportFormat,
)

__all__ = [
    # Common
    "GrammarPoint",
    "Vocabulary",
    "TBCLLevel",
    "ArticleType",
    "QuestionType",
    # Generate
    "GenerateArticleRequest",
    "GenerateArticleResponse",
    "GenerateQuestionsRequest",
    "GenerateQuestionsResponse",
    "Question",
    # Validate
    "ValidateRequest",
    "ValidateResponse",
    "GrammarCheckResult",
    "VocabCheckResult",
    # Export
    "ExportRequest",
    "ExportResponse",
    "ExportFormat",
]
