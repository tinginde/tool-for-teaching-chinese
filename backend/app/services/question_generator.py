"""
Question generation service using Claude API.
"""

import asyncio
import time
import json
from typing import List, Dict, Optional
from anthropic import AsyncAnthropic

from ..schemas.generate import Question
from ..schemas.common import QuestionType
from ..config import get_anthropic_api_key, get_settings


class QuestionGenerator:
    """Service for generating reading comprehension questions using Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the question generator.

        Args:
            api_key: Anthropic API key. If not provided, will try to get from env.
        """
        self.api_key = api_key or get_anthropic_api_key()
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for question generation")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.settings = get_settings()

    def _build_generation_prompt(
        self,
        article_text: str,
        num_questions: int,
        question_types: Optional[List[QuestionType]] = None,
        focus_areas: Optional[List[str]] = None,
    ) -> str:
        """Build the prompt for question generation."""

        # Default question types
        if not question_types:
            question_types = [QuestionType.MULTIPLE_CHOICE]

        # Question type descriptions
        type_instructions = {
            QuestionType.MULTIPLE_CHOICE: "選擇題（4個選項，1個正確答案）",
            QuestionType.FILL_IN_BLANK: "填空題（挖空文章中的關鍵詞）",
            QuestionType.SHORT_ANSWER: "簡答題（需要簡短回答）",
            QuestionType.MATCHING: "配對題（將相關項目配對）",
            QuestionType.ORDERING: "排序題（按正確順序排列）",
        }

        types_str = "\n".join([f"- {type_instructions[qt]}" for qt in question_types])

        # Focus areas
        focus_str = ""
        if focus_areas:
            focus_str = f"\n\n## 重點考核領域\n" + "\n".join([f"- {area}" for area in focus_areas])

        prompt = f"""請根據以下文章，生成 {num_questions} 道閱讀理解題目。

## 文章內容
{article_text}

## 題目類型
{types_str}
{focus_str}

## 題目要求
1. **題目分佈**:
   - 細節理解題：直接從文章中找到答案
   - 推論題：需要理解文章含義並推理
   - 詞彙題：測試對生詞的理解

2. **難度適中**: 符合文章的難度等級

3. **選項設計**（選擇題）:
   - 4個選項
   - 只有1個正確答案
   - 干擾選項要有合理性，不能太明顯錯誤

4. **答案解析**: 每題都要提供簡短的解析說明

## 輸出格式
請以 JSON 格式輸出，格式如下：

```json
{{
  "questions": [
    {{
      "question_text": "題目文字",
      "question_type": "multiple_choice",
      "options": ["選項A", "選項B", "選項C", "選項D"],
      "correct_answer": "正確答案",
      "explanation": "答案解析",
      "difficulty": "easy/medium/hard"
    }}
  ]
}}
```

請直接輸出 JSON，不要有任何其他文字。
"""
        return prompt

    async def generate_questions(
        self,
        article_text: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None,
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """
        Generate reading comprehension questions based on an article.

        Args:
            article_text: The article text
            num_questions: Number of questions to generate
            question_types: Types of questions to generate
            focus_areas: Areas to focus on (e.g., 'vocabulary', 'grammar')

        Returns:
            Dict with keys:
                - questions: List of Question objects
                - generation_time: Time taken in seconds
        """
        start_time = time.time()

        # Build prompt
        prompt = self._build_generation_prompt(
            article_text=article_text,
            num_questions=num_questions,
            question_types=question_types,
            focus_areas=focus_areas,
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
                temperature=0.7,
            )

            # Extract and parse JSON
            response_text = response.content[0].text.strip()

            # Try to find JSON in the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            # Parse JSON
            result = json.loads(response_text)

            # Convert to Question objects
            questions = [Question(**q) for q in result["questions"]]

            generation_time = time.time() - start_time

            return {
                "questions": questions,
                "generation_time": generation_time,
            }

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse question JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate questions: {str(e)}")

    def generate_questions_sync(self, *args, **kwargs) -> Dict[str, any]:
        """Synchronous wrapper for generate_questions."""
        return asyncio.run(self.generate_questions(*args, **kwargs))
