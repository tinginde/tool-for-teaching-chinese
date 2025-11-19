"""
API routes for content export.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from ..schemas.export import ExportRequest, ExportResponse, ExportFormat
from ..services import ExportService

router = APIRouter()


@router.post(
    "/",
    response_model=ExportResponse,
    summary="Export content",
    description="Export article and questions to various formats (HTML, TXT, JSON)"
)
async def export_content(request: ExportRequest):
    """
    Export content to the specified format.

    - **article_text**: The article text to export
    - **questions**: Optional questions to include
    - **validation_result**: Optional validation result to include
    - **format**: Export format (html, txt, json)
    - **include_answers**: Whether to include answers (for questions)
    - **include_validation**: Whether to include validation report
    - **title**: Optional document title

    Returns the exported content as a string with suggested filename.
    """
    try:
        export_service = ExportService()

        # Convert questions to dict format
        questions_dict = None
        if request.questions:
            questions_dict = [
                q if isinstance(q, dict) else q.dict()
                for q in request.questions
            ]

        # Perform export
        content, filename = export_service.export(
            article_text=request.article_text,
            format=request.format,
            questions=questions_dict,
            validation_result=request.validation_result,
            include_answers=request.include_answers,
            include_validation=request.include_validation,
            title=request.title,
        )

        return ExportResponse(
            content=content,
            format=request.format,
            filename=filename,
            size_bytes=len(content.encode('utf-8')),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post(
    "/download",
    summary="Download exported content",
    description="Export and download content as a file"
)
async def download_content(request: ExportRequest):
    """
    Export content and return as downloadable file.

    Same parameters as /export/ but returns actual file response.
    """
    try:
        export_service = ExportService()

        # Convert questions to dict format
        questions_dict = None
        if request.questions:
            questions_dict = [
                q if isinstance(q, dict) else q.dict()
                for q in request.questions
            ]

        # Perform export
        content, filename = export_service.export(
            article_text=request.article_text,
            format=request.format,
            questions=questions_dict,
            validation_result=request.validation_result,
            include_answers=request.include_answers,
            include_validation=request.include_validation,
            title=request.title,
        )

        # Determine media type
        media_types = {
            ExportFormat.HTML: "text/html",
            ExportFormat.TXT: "text/plain",
            ExportFormat.JSON: "application/json",
        }

        media_type = media_types.get(request.format, "text/plain")

        return Response(
            content=content.encode('utf-8'),
            media_type=f"{media_type}; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )
