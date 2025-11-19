"""
Common schemas used across multiple API endpoints.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TBCLLevel(str, Enum):
    """TBCL (Taiwan Benchmark for Chinese Language) levels."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class ArticleType(str, Enum):
    """Types of articles to generate."""
    DAILY_LIFE = "daily_life"           # 日常生活故事
    TAIWAN_CULTURE = "taiwan_culture"   # 台灣文化介紹
    NEWS = "news"                       # 簡化新聞報導
    INTERVIEW = "interview"             # 人物訪談


class QuestionType(str, Enum):
    """Types of reading comprehension questions."""
    MULTIPLE_CHOICE = "multiple_choice"  # 選擇題
    FILL_IN_BLANK = "fill_in_blank"     # 填空題
    SHORT_ANSWER = "short_answer"       # 問答題
    MATCHING = "matching"               # 配對題
    ORDERING = "ordering"               # 排序題


class GrammarPoint(BaseModel):
    """A grammar point to be included in the article."""
    name: str = Field(..., description="Grammar point name (e.g., '把字句', '被動句')")
    description: Optional[str] = Field(None, description="Optional description or example")
    tbcl_level: Optional[TBCLLevel] = Field(None, description="TBCL level of this grammar point")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "把字句",
                "description": "把 + Object + Verb",
                "tbcl_level": "A2"
            }
        }


class Vocabulary(BaseModel):
    """A vocabulary word to be included in the article."""
    word: str = Field(..., description="The vocabulary word")
    pos: Optional[str] = Field(None, description="Part of speech (N, V, Adj, Adv, etc.)")
    definition: Optional[str] = Field(None, description="Definition or translation")
    tbcl_level: Optional[TBCLLevel] = Field(None, description="TBCL level of this word")

    class Config:
        json_schema_extra = {
            "example": {
                "word": "環境",
                "pos": "N",
                "definition": "environment",
                "tbcl_level": "A2"
            }
        }
