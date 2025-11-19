"""
Article generation service using Claude API.
"""

import asyncio
import time
from typing import List, Dict, Optional
from anthropic import AsyncAnthropic

from ..schemas.common import GrammarPoint, Vocabulary, ArticleType, TBCLLevel
from ..config import get_anthropic_api_key, get_settings


class ArticleGenerator:
    """Service for generating Chinese teaching articles using Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the article generator.

        Args:
            api_key: Anthropic API key. If not provided, will try to get from env.
        """
        self.api_key = api_key or get_anthropic_api_key()
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for article generation")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.settings = get_settings()

    def _build_generation_prompt(
        self,
        grammar_points: List[GrammarPoint],
        vocabulary: List[Vocabulary],
        article_type: ArticleType,
        tbcl_level: TBCLLevel,
        length: int,
        topic: Optional[str] = None,
    ) -> str:
        """Build the prompt for article generation."""

        # Grammar points list
        grammar_list = "\n".join([
            f"- {gp.name}" + (f" ({gp.description})" if gp.description else "")
            for gp in grammar_points
        ])

        # Vocabulary list
        vocab_list = "\n".join([
            f"- {v.word}" + (f" ({v.pos})" if v.pos else "") +
            (f" - {v.definition}" if v.definition else "")
            for v in vocabulary
        ])

        # Article type description
        type_descriptions = {
            ArticleType.DAILY_LIFE: "日常生活故事，描述真實的生活場景和經驗",
            ArticleType.TAIWAN_CULTURE: "台灣文化介紹，介紹台灣的文化、習俗或特色",
            ArticleType.NEWS: "簡化新聞報導，改寫新聞成適合學習者的文章",
            ArticleType.INTERVIEW: "人物訪談，採訪對話形式的文章",
        }

        # TBCL level description
        level_descriptions = {
            TBCLLevel.A1: "入門級（150詞彙量），使用最簡單的句型和詞彙",
            TBCLLevel.A2: "基礎級（300詞彙量），使用基本句型，語法簡單",
            TBCLLevel.B1: "進階級（600詞彙量），語法稍微複雜，詞彙更豐富",
            TBCLLevel.B2: "高階級（1200詞彙量），句式多樣，詞彙廣泛",
            TBCLLevel.C1: "流利級（2500詞彙量），接近母語者水平",
            TBCLLevel.C2: "精通級（5000+詞彙量），完全自如運用中文",
        }

        topic_instruction = f"\n\n## 主題\n{topic}" if topic else ""

        prompt = f"""請根據以下要求，生成一篇適合華語教學的文章。

## 文章類型
{type_descriptions[article_type]}

## 目標難度等級
{tbcl_level.value} - {level_descriptions[tbcl_level]}

## 必須包含的語法點
{grammar_list}

**重要**: 每個語法點必須在文章中至少出現一次，且使用正確。

## 必須包含的生詞
{vocab_list}

**重要**: 每個生詞必須在文章中至少出現一次。
{topic_instruction}

## 文章要求
1. **長度**: 約 {length} 字（{length - 50} 到 {length + 50} 字之間）
2. **內容要求**:
   - 內容有趣、有意義、連貫
   - 符合 {tbcl_level.value} 等級的難度
   - 語法正確，用詞恰當
   - 適合教學使用
3. **結構要求**:
   - 有明確的開頭、中間、結尾
   - 段落分明（2-4 段）
   - 邏輯清晰

## 特別注意
1. **語法點使用**: 確保每個指定的語法點都正確使用，並且自然融入文章
2. **生詞使用**: 確保每個指定的生詞都出現在文章中
3. **難度控制**: 除了指定的生詞外，其他詞彙應符合 {tbcl_level.value} 等級
4. **文化適切性**: 內容應符合台灣華語文化背景

請直接輸出文章內容，不需要任何額外說明或標註。
"""
        return prompt

    async def generate_article(
        self,
        grammar_points: List[GrammarPoint],
        vocabulary: List[Vocabulary],
        article_type: ArticleType = ArticleType.DAILY_LIFE,
        tbcl_level: TBCLLevel = TBCLLevel.A2,
        length: int = 400,
        topic: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Generate an article based on the given parameters.

        Args:
            grammar_points: List of grammar points to include
            vocabulary: List of vocabulary words to include
            article_type: Type of article to generate
            tbcl_level: Target TBCL difficulty level
            length: Desired article length in characters
            topic: Optional topic or theme

        Returns:
            Dict with keys:
                - article_text: The generated article
                - word_count: Actual character count
                - generation_time: Time taken in seconds
        """
        start_time = time.time()

        # Build prompt
        prompt = self._build_generation_prompt(
            grammar_points=grammar_points,
            vocabulary=vocabulary,
            article_type=article_type,
            tbcl_level=tbcl_level,
            length=length,
            topic=topic,
        )

        # Call Claude API
        try:
            response = await self.client.messages.create(
                model=self.settings.ANTHROPIC_MODEL,
                max_tokens=self.settings.ANTHROPIC_MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Some creativity but not too random
            )

            # Extract article text
            article_text = response.content[0].text.strip()

            # Calculate metrics
            word_count = len(article_text)
            generation_time = time.time() - start_time

            return {
                "article_text": article_text,
                "word_count": word_count,
                "generation_time": generation_time,
            }

        except Exception as e:
            raise Exception(f"Failed to generate article: {str(e)}")

    def generate_article_sync(self, *args, **kwargs) -> Dict[str, any]:
        """Synchronous wrapper for generate_article."""
        return asyncio.run(self.generate_article(*args, **kwargs))
