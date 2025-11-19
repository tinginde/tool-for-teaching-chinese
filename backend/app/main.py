"""
FastAPI main application for the Chinese Teaching Tool.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import api_router
from .config import get_settings

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    華語教材智能生成器 API

    ## 核心功能

    ### 1. 文章生成 (Generate)
    - **POST /api/v1/generate/article**: 根據語法點和生詞生成教學文章
    - **POST /api/v1/generate/questions**: 根據文章生成閱讀理解題目

    ### 2. 準確性驗證 (Validate) ⭐ 核心特色
    - **POST /api/v1/validate/**: 驗證文章是否包含指定的語法點和生詞
    - 支援規則匹配 + AI 語義分析雙重驗證
    - 提供精確的位置信息用於視覺化標註

    ### 3. 內容匯出 (Export)
    - **POST /api/v1/export/**: 匯出文章和題目為多種格式 (HTML, TXT, JSON)
    - **POST /api/v1/export/download**: 下載匯出的文件

    ## 技術特色
    - 使用 Anthropic Claude API 生成高品質內容
    - 混合式驗證引擎：規則匹配 + AI 驗證
    - 支援 TBCL (台灣華語文能力基準) 等級
    - 30+ 常見語法點檢測
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "message": "歡迎使用華語教材智能生成器 API！請訪問 /docs 查看完整的 API 文檔。"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )
