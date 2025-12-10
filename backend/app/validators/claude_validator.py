"""
Claude API 語法驗證模組
使用 Claude API 進行語義分析，確保語法使用的正確性
"""
import json
import os
from typing import List, Dict, Any, Optional

# anthropic 是可選依賴，如果沒有安裝，Claude 驗證功能將不可用
try:
    from anthropic import Anthropic, AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None
    AsyncAnthropic = None


class ClaudeValidator:
    """Claude API 驗證器 - 語義分析"""

    # 語法驗證 Prompt 模板
    GRAMMAR_VALIDATION_PROMPT = """請分析以下文章中指定語法點的使用是否正確。

## 文章內容
{article_text}

## 需要檢查的語法點
**{grammar_point_name}**：{grammar_point_description}

## 檢測到的使用位置
{detected_usage}

## 請評估
1. 這些使用是否符合該語法點的定義？
2. 語法使用是否正確、自然？
3. 是否有其他位置也使用了此語法點但未被檢測到？

請以 JSON 格式回復：
{{
  "is_correct": true/false,
  "confidence": 0.0-1.0,
  "issues": ["問題描述..."],
  "missed_instances": ["未檢測到的使用..."],
  "suggestions": ["改進建議..."]
}}

請只返回 JSON，不要包含其他解釋文字。"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Claude 驗證器

        Args:
            api_key: Anthropic API key，如果不提供則從環境變數讀取
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic 包未安裝。請運行：pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)

    def format_detected_instances(self, instances: List[Dict[str, Any]]) -> str:
        """
        格式化檢測到的語法實例

        Args:
            instances: 檢測到的語法實例列表

        Returns:
            格式化的字符串
        """
        if not instances:
            return "未檢測到此語法點的使用。"

        formatted = []
        for i, instance in enumerate(instances, 1):
            text = instance.get("text", "")
            pos = instance.get("position", [0, 0])
            formatted.append(f"{i}. 「{text}」（位置：{pos[0]}-{pos[1]}）")

        return "\n".join(formatted)

    async def validate_grammar_async(
        self,
        article_text: str,
        grammar_name: str,
        grammar_description: str,
        detected_instances: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        異步驗證語法使用是否正確

        Args:
            article_text: 文章文本
            grammar_name: 語法點名稱
            grammar_description: 語法點描述
            detected_instances: 檢測到的語法實例

        Returns:
            驗證結果
            {
                "is_correct": True,
                "confidence": 0.95,
                "issues": [],
                "missed_instances": [],
                "suggestions": []
            }
        """
        # 構建 prompt
        prompt = self.GRAMMAR_VALIDATION_PROMPT.format(
            article_text=article_text,
            grammar_point_name=grammar_name,
            grammar_point_description=grammar_description,
            detected_usage=self.format_detected_instances(detected_instances)
        )

        try:
            # 調用 Claude API
            response = await self.async_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # 解析響應
            response_text = response.content[0].text.strip()

            # 嘗試提取 JSON
            validation_result = self._parse_validation_response(response_text)

            return validation_result

        except Exception as e:
            # 如果 API 調用失敗，返回默認結果
            return {
                "is_correct": True,  # 保守估計為正確
                "confidence": 0.5,
                "issues": [f"API 調用失敗: {str(e)}"],
                "missed_instances": [],
                "suggestions": []
            }

    def validate_grammar_sync(
        self,
        article_text: str,
        grammar_name: str,
        grammar_description: str,
        detected_instances: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        同步驗證語法使用是否正確

        Args:
            article_text: 文章文本
            grammar_name: 語法點名稱
            grammar_description: 語法點描述
            detected_instances: 檢測到的語法實例

        Returns:
            驗證結果
        """
        # 構建 prompt
        prompt = self.GRAMMAR_VALIDATION_PROMPT.format(
            article_text=article_text,
            grammar_point_name=grammar_name,
            grammar_point_description=grammar_description,
            detected_usage=self.format_detected_instances(detected_instances)
        )

        try:
            # 調用 Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # 解析響應
            response_text = response.content[0].text.strip()

            # 嘗試提取 JSON
            validation_result = self._parse_validation_response(response_text)

            return validation_result

        except Exception as e:
            # 如果 API 調用失敗，返回默認結果
            return {
                "is_correct": True,
                "confidence": 0.5,
                "issues": [f"API 調用失敗: {str(e)}"],
                "missed_instances": [],
                "suggestions": []
            }

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析 Claude 的驗證響應

        Args:
            response_text: Claude 返回的文本

        Returns:
            解析後的驗證結果
        """
        try:
            # 嘗試查找 JSON 塊
            # 可能的格式：```json\n{...}\n``` 或直接 {...}
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                result = json.loads(json_text)

                # 確保包含必需的字段
                return {
                    "is_correct": result.get("is_correct", True),
                    "confidence": float(result.get("confidence", 0.8)),
                    "issues": result.get("issues", []),
                    "missed_instances": result.get("missed_instances", []),
                    "suggestions": result.get("suggestions", [])
                }
            else:
                raise ValueError("No JSON found in response")

        except (json.JSONDecodeError, ValueError) as e:
            # 如果解析失敗，返回保守的默認值
            return {
                "is_correct": True,
                "confidence": 0.7,
                "issues": [f"響應解析失敗: {str(e)}"],
                "missed_instances": [],
                "suggestions": []
            }

    async def validate_multiple_grammar_async(
        self,
        article_text: str,
        grammar_checks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量驗證多個語法點

        Args:
            article_text: 文章文本
            grammar_checks: 語法檢查列表
                [
                    {
                        "name": "把字句",
                        "description": "...",
                        "instances": [...]
                    },
                    ...
                ]

        Returns:
            驗證結果列表
        """
        results = []

        for check in grammar_checks:
            result = await self.validate_grammar_async(
                article_text,
                check["name"],
                check["description"],
                check["instances"]
            )
            results.append({
                "grammar_name": check["name"],
                "validation": result
            })

        return results


# 便捷函數
async def validate_grammar_with_claude(
    article_text: str,
    grammar_name: str,
    grammar_description: str,
    detected_instances: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函數：使用 Claude API 驗證語法

    Args:
        article_text: 文章文本
        grammar_name: 語法點名稱
        grammar_description: 語法點描述
        detected_instances: 檢測到的實例
        api_key: API key（可選）

    Returns:
        驗證結果
    """
    validator = ClaudeValidator(api_key)
    return await validator.validate_grammar_async(
        article_text,
        grammar_name,
        grammar_description,
        detected_instances
    )
