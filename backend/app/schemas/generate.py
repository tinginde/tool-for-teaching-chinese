"""
Schemas for article and question generation endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .common import GrammarPoint, Vocabulary, ArticleType, TBCLLevel, QuestionType


class GenerateArticleRequest(BaseModel):
    """Request model for generating an article."""
    grammar_points: List[GrammarPoint] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of grammar points to include (1-5)"
    )
    vocabulary: List[Vocabulary] = Field(
        ...,
        min_length=5,
        max_length=20,
        description="List of vocabulary words to include (5-20)"
    )
    article_type: ArticleType = Field(
        default=ArticleType.DAILY_LIFE,
        description="Type of article to generate"
    )
    tbcl_level: TBCLLevel = Field(
        default=TBCLLevel.A2,
        description="Target TBCL difficulty level"
    )
    length: int = Field(
        default=400,
        ge=300,
        le=600,
        description="Desired article length in characters (300-600)"
    )
    topic: Optional[str] = Field(
        None,
        description="Optional topic or theme for the article"
    )
    auto_validate: bool = Field(
        default=True,
        description="Automatically validate the generated article"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "grammar_points": [
                    {"name": "把字句", "tbcl_level": "A2"},
                    {"name": "比較句", "tbcl_level": "A2"}
                ],
                "vocabulary": [
                    {"word": "環境", "pos": "N"},
                    {"word": "保護", "pos": "V"},
                    {"word": "垃圾", "pos": "N"}
                ],
                "article_type": "daily_life",
                "tbcl_level": "A2",
                "length": 400,
                "topic": "環保生活",
                "auto_validate": True
            }
        }


class GenerateArticleResponse(BaseModel):
    """Response model for article generation."""
    article_text: str = Field(..., description="The generated article text")
    word_count: int = Field(..., description="Actual word count")
    validation_result: Optional[dict] = Field(
        None,
        description="Validation result if auto_validate=True"
    )
    generation_time: float = Field(..., description="Time taken to generate (seconds)")
    article_id: Optional[str] = Field(None, description="Unique identifier for this article")

    class Config:
        json_schema_extra = {
            "example": {
                "article_text": "今天天氣很好，我把房間打掃乾淨...",
                "word_count": 387,
                "validation_result": {
                    "overall_pass": True,
                    "grammar_check": [],
                    "vocab_check": []
                },
                "generation_time": 3.45,
                "article_id": "art_abc123"
            }
        }


class Question(BaseModel):
    """A single question model."""
    question_text: str = Field(..., description="The question text")
    question_type: QuestionType = Field(..., description="Type of question")
    options: Optional[List[str]] = Field(None, description="Answer options (for multiple choice)")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: Optional[str] = Field(None, description="Explanation of the answer")
    difficulty: Optional[str] = Field(None, description="Question difficulty level")

    class Config:
        json_schema_extra = {
            "example": {
                "question_text": "文章中提到的主要問題是什麼？",
                "question_type": "multiple_choice",
                "options": ["環境污染", "交通問題", "天氣變化", "經濟發展"],
                "correct_answer": "環境污染",
                "explanation": "文章開頭就提到了環境污染的嚴重性。",
                "difficulty": "medium"
            }
        }


class GenerateQuestionsRequest(BaseModel):
    """Request model for generating questions."""
    article_text: str = Field(..., description="The article text to base questions on")
    num_questions: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of questions to generate (1-10)"
    )
    question_types: Optional[List[QuestionType]] = Field(
        None,
        description="Types of questions to generate (default: mixed)"
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Areas to focus on (e.g., 'vocabulary', 'grammar', 'comprehension')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "article_text": "今天天氣很好...",
                "num_questions": 5,
                "question_types": ["multiple_choice"],
                "focus_areas": ["comprehension", "vocabulary"]
            }
        }


class GenerateQuestionsResponse(BaseModel):
    """Response model for question generation."""
    questions: List[Question] = Field(..., description="List of generated questions")
    generation_time: float = Field(..., description="Time taken to generate (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "question_text": "文章中提到的主要問題是什麼？",
                        "question_type": "multiple_choice",
                        "options": ["環境污染", "交通問題", "天氣變化", "經濟發展"],
                        "correct_answer": "環境污染",
                        "explanation": "文章開頭就提到了環境污染的嚴重性。"
                    }
                ],
                "generation_time": 2.3
            }
        }
