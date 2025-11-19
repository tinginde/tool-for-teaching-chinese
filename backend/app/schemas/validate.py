"""
Schemas for validation endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .common import GrammarPoint, Vocabulary


class ValidateRequest(BaseModel):
    """Request model for validating an article."""
    article_text: str = Field(..., description="The article text to validate")
    grammar_points: List[GrammarPoint] = Field(
        ...,
        description="Grammar points that should appear in the article"
    )
    vocabulary: List[Vocabulary] = Field(
        ...,
        description="Vocabulary words that should appear in the article"
    )
    use_claude_validation: bool = Field(
        default=False,
        description="Use Claude API for semantic validation (slower but more accurate)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "article_text": "今天我把房間打掃乾淨了。天氣比昨天更熱...",
                "grammar_points": [
                    {"name": "把字句"},
                    {"name": "比較句"}
                ],
                "vocabulary": [
                    {"word": "房間"},
                    {"word": "打掃"},
                    {"word": "天氣"}
                ],
                "use_claude_validation": True
            }
        }


class GrammarCheckResult(BaseModel):
    """Result of grammar point checking."""
    name: str = Field(..., description="Grammar point name")
    found: bool = Field(..., description="Whether the grammar point was found")
    count: int = Field(..., description="Number of times it appears")
    positions: List[List[int]] = Field(
        default_factory=list,
        description="Positions where it appears [[start, end], ...]"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Examples of usage found in the text"
    )
    correct: Optional[bool] = Field(
        None,
        description="Whether the usage is correct (if Claude validation is used)"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score (0-1) if Claude validation is used"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="Issues found with the usage"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "把字句",
                "found": True,
                "count": 2,
                "positions": [[4, 12], [28, 36]],
                "examples": ["把房間打掃乾淨", "把書放在桌上"],
                "correct": True,
                "confidence": 0.95,
                "issues": [],
                "suggestions": []
            }
        }


class VocabCheckResult(BaseModel):
    """Result of vocabulary checking."""
    word: str = Field(..., description="The vocabulary word")
    found: bool = Field(..., description="Whether the word was found")
    count: int = Field(..., description="Number of times it appears")
    positions: List[List[int]] = Field(
        default_factory=list,
        description="Positions where it appears [[start, end], ...]"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "word": "環境",
                "found": True,
                "count": 3,
                "positions": [[12, 14], [45, 47], [89, 91]]
            }
        }


class ValidateResponse(BaseModel):
    """Response model for validation."""
    overall_pass: bool = Field(..., description="Whether the article passes validation")
    grammar_check: List[GrammarCheckResult] = Field(
        ...,
        description="Results of grammar point checking"
    )
    vocab_check: List[VocabCheckResult] = Field(
        ...,
        description="Results of vocabulary checking"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about missing or incorrect elements"
    )
    statistics: dict = Field(
        ...,
        description="Overall statistics (pass rates, etc.)"
    )
    validation_time: float = Field(..., description="Time taken to validate (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "overall_pass": True,
                "grammar_check": [
                    {
                        "name": "把字句",
                        "found": True,
                        "count": 2,
                        "positions": [[4, 12], [28, 36]],
                        "examples": ["把房間打掃乾淨", "把書放在桌上"]
                    }
                ],
                "vocab_check": [
                    {
                        "word": "環境",
                        "found": True,
                        "count": 3,
                        "positions": [[12, 14], [45, 47], [89, 91]]
                    }
                ],
                "warnings": [],
                "statistics": {
                    "grammar_pass_rate": 1.0,
                    "vocab_pass_rate": 1.0
                },
                "validation_time": 1.23
            }
        }
