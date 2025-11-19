"""
API routes for content generation (articles and questions).
"""

import time
import uuid
from fastapi import APIRouter, HTTPException, status

from ..schemas.generate import (
    GenerateArticleRequest,
    GenerateArticleResponse,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
)
from ..services import ArticleGenerator, QuestionGenerator
from ..validators import ValidationEngine
from ..config import get_anthropic_api_key

router = APIRouter()


@router.post(
    "/article",
    response_model=GenerateArticleResponse,
    summary="Generate an article",
    description="Generate a Chinese teaching article based on grammar points and vocabulary"
)
async def generate_article(request: GenerateArticleRequest):
    """
    Generate an article based on specified grammar points and vocabulary.

    - **grammar_points**: List of grammar points to include (1-5)
    - **vocabulary**: List of vocabulary words to include (5-20)
    - **article_type**: Type of article (daily_life, taiwan_culture, news, interview)
    - **tbcl_level**: Target difficulty level (A1-C2)
    - **length**: Desired length in characters (300-600)
    - **topic**: Optional topic or theme
    - **auto_validate**: Whether to automatically validate the generated article

    Returns the generated article with optional validation results.
    """
    try:
        # Initialize article generator
        api_key = get_anthropic_api_key()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ANTHROPIC_API_KEY is not configured"
            )

        generator = ArticleGenerator(api_key=api_key)

        # Generate article
        result = await generator.generate_article(
            grammar_points=request.grammar_points,
            vocabulary=request.vocabulary,
            article_type=request.article_type,
            tbcl_level=request.tbcl_level,
            length=request.length,
            topic=request.topic,
        )

        article_text = result["article_text"]
        word_count = result["word_count"]
        generation_time = result["generation_time"]

        # Optional validation
        validation_result = None
        if request.auto_validate:
            try:
                validator = ValidationEngine(api_key=api_key)
                validation_start = time.time()

                # Use quick validation (without Claude API) for speed
                validation_result = validator.quick_validation(
                    article_text=article_text,
                    grammar_points=[
                        {"name": gp.name, "description": gp.description}
                        for gp in request.grammar_points
                    ],
                    vocabulary=[
                        {"word": v.word, "pos": v.pos}
                        for v in request.vocabulary
                    ],
                )

                validation_result["validation_time"] = time.time() - validation_start

            except Exception as e:
                # Don't fail the whole request if validation fails
                validation_result = {
                    "error": f"Validation failed: {str(e)}",
                    "overall_pass": None,
                }

        # Generate unique article ID
        article_id = f"art_{uuid.uuid4().hex[:12]}"

        return GenerateArticleResponse(
            article_text=article_text,
            word_count=word_count,
            validation_result=validation_result,
            generation_time=generation_time,
            article_id=article_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate article: {str(e)}"
        )


@router.post(
    "/questions",
    response_model=GenerateQuestionsResponse,
    summary="Generate questions",
    description="Generate reading comprehension questions based on an article"
)
async def generate_questions(request: GenerateQuestionsRequest):
    """
    Generate reading comprehension questions based on an article.

    - **article_text**: The article text to base questions on
    - **num_questions**: Number of questions to generate (1-10)
    - **question_types**: Types of questions (optional, defaults to multiple_choice)
    - **focus_areas**: Areas to focus on (optional, e.g., 'vocabulary', 'grammar')

    Returns a list of generated questions with answers and explanations.
    """
    try:
        # Initialize question generator
        api_key = get_anthropic_api_key()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ANTHROPIC_API_KEY is not configured"
            )

        generator = QuestionGenerator(api_key=api_key)

        # Generate questions
        result = await generator.generate_questions(
            article_text=request.article_text,
            num_questions=request.num_questions,
            question_types=request.question_types,
            focus_areas=request.focus_areas,
        )

        return GenerateQuestionsResponse(
            questions=result["questions"],
            generation_time=result["generation_time"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )
