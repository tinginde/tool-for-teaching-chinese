"""
API routes for content validation.
"""

import time
from fastapi import APIRouter, HTTPException, status

from ..schemas.validate import ValidateRequest, ValidateResponse
from ..validators import ValidationEngine
from ..config import get_anthropic_api_key

router = APIRouter()


@router.post(
    "/",
    response_model=ValidateResponse,
    summary="Validate article",
    description="Validate that an article contains the required grammar points and vocabulary"
)
async def validate_article(request: ValidateRequest):
    """
    Validate an article for accuracy.

    This is the **core competitive advantage feature** of this tool.

    - **article_text**: The article text to validate
    - **grammar_points**: Grammar points that should appear in the article
    - **vocabulary**: Vocabulary words that should appear in the article
    - **use_claude_validation**: Use Claude API for semantic validation (slower but more accurate)

    Returns detailed validation results including:
    - Grammar point detection results with positions
    - Vocabulary detection results with positions
    - Overall pass/fail status
    - Warnings for missing elements
    - Statistics (pass rates)
    """
    try:
        start_time = time.time()

        # Initialize validation engine
        api_key = None
        if request.use_claude_validation:
            api_key = get_anthropic_api_key()
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ANTHROPIC_API_KEY is required for Claude validation. "
                           "Set use_claude_validation=False to use basic validation."
                )

        validator = ValidationEngine(api_key=api_key)

        # Prepare grammar points and vocabulary
        grammar_points = [
            {"name": gp.name, "description": gp.description}
            for gp in request.grammar_points
        ]

        vocabulary = [
            {"word": v.word, "pos": v.pos}
            for v in request.vocabulary
        ]

        # Perform validation
        if request.use_claude_validation:
            # Comprehensive validation with Claude API
            result = await validator.comprehensive_validation(
                article_text=request.article_text,
                grammar_points=grammar_points,
                vocabulary=vocabulary,
                use_claude_validation=True,
            )
        else:
            # Quick validation without Claude API
            result = validator.quick_validation(
                article_text=request.article_text,
                grammar_points=grammar_points,
                vocabulary=vocabulary,
            )

        validation_time = time.time() - start_time

        return ValidateResponse(
            overall_pass=result["overall_pass"],
            grammar_check=result["grammar_check"],
            vocab_check=result["vocab_check"],
            warnings=result.get("warnings", []),
            statistics=result.get("statistics", {}),
            validation_time=validation_time,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
