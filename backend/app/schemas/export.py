"""
Schemas for export endpoints.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Export format options."""
    HTML = "html"
    TXT = "txt"
    JSON = "json"
    PDF = "pdf"      # Future enhancement
    DOCX = "docx"    # Future enhancement


class ExportRequest(BaseModel):
    """Request model for exporting content."""
    article_text: str = Field(..., description="The article text to export")
    questions: Optional[List[dict]] = Field(None, description="Questions to include")
    validation_result: Optional[dict] = Field(None, description="Validation result to include")
    format: ExportFormat = Field(default=ExportFormat.HTML, description="Export format")
    include_answers: bool = Field(default=True, description="Include answers in export")
    include_validation: bool = Field(default=False, description="Include validation report")
    title: Optional[str] = Field(None, description="Document title")

    class Config:
        json_schema_extra = {
            "example": {
                "article_text": "今天天氣很好...",
                "questions": [
                    {
                        "question_text": "文章的主題是什麼？",
                        "options": ["天氣", "環境", "學習", "旅行"],
                        "correct_answer": "天氣"
                    }
                ],
                "format": "html",
                "include_answers": True,
                "include_validation": False,
                "title": "閱讀理解練習"
            }
        }


class ExportResponse(BaseModel):
    """Response model for export."""
    content: str = Field(..., description="The exported content")
    format: ExportFormat = Field(..., description="Format of the exported content")
    filename: str = Field(..., description="Suggested filename for download")
    size_bytes: int = Field(..., description="Size of the content in bytes")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "<html><body>...",
                "format": "html",
                "filename": "article_20251118.html",
                "size_bytes": 4523
            }
        }
