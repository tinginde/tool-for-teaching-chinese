"""
Claude API 语法验证模块
使用 Claude API 进行语义分析，确保语法使用的正确性
"""
import json
import os
from typing import List, Dict, Any, Optional

# anthropic 是可选依赖，如果没有安装，Claude 验证功能将不可用
try:
    from anthropic import Anthropic, AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None
    AsyncAnthropic = None


class ClaudeValidator:
    """Claude API 验证器 - 语义分析"""

    # 语法验证 Prompt 模板
    GRAMMAR_VALIDATION_PROMPT = """请分析以下文章中指定语法点的使用是否正确。

## 文章内容
{article_text}

## 需要检查的语法点
**{grammar_point_name}**：{grammar_point_description}

## 检测到的使用位置
{detected_usage}

## 请评估
1. 这些使用是否符合该语法点的定义？
2. 语法使用是否正确、自然？
3. 是否有其他位置也使用了此语法点但未被检测到？

请以 JSON 格式回复：
{{
  "is_correct": true/false,
  "confidence": 0.0-1.0,
  "issues": ["问题描述..."],
  "missed_instances": ["未检测到的使用..."],
  "suggestions": ["改进建议..."]
}}

请只返回 JSON，不要包含其他解释文字。"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Claude 验证器

        Args:
            api_key: Anthropic API key，如果不提供则从环境变量读取
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic 包未安装。请运行：pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)

    def format_detected_instances(self, instances: List[Dict[str, Any]]) -> str:
        """
        格式化检测到的语法实例

        Args:
            instances: 检测到的语法实例列表

        Returns:
            格式化的字符串
        """
        if not instances:
            return "未检测到此语法点的使用。"

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
        异步验证语法使用是否正确

        Args:
            article_text: 文章文本
            grammar_name: 语法点名称
            grammar_description: 语法点描述
            detected_instances: 检测到的语法实例

        Returns:
            验证结果
            {
                "is_correct": True,
                "confidence": 0.95,
                "issues": [],
                "missed_instances": [],
                "suggestions": []
            }
        """
        # 构建 prompt
        prompt = self.GRAMMAR_VALIDATION_PROMPT.format(
            article_text=article_text,
            grammar_point_name=grammar_name,
            grammar_point_description=grammar_description,
            detected_usage=self.format_detected_instances(detected_instances)
        )

        try:
            # 调用 Claude API
            response = await self.async_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # 解析响应
            response_text = response.content[0].text.strip()

            # 尝试提取 JSON
            validation_result = self._parse_validation_response(response_text)

            return validation_result

        except Exception as e:
            # 如果 API 调用失败，返回默认结果
            return {
                "is_correct": True,  # 保守估计为正确
                "confidence": 0.5,
                "issues": [f"API 调用失败: {str(e)}"],
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
        同步验证语法使用是否正确

        Args:
            article_text: 文章文本
            grammar_name: 语法点名称
            grammar_description: 语法点描述
            detected_instances: 检测到的语法实例

        Returns:
            验证结果
        """
        # 构建 prompt
        prompt = self.GRAMMAR_VALIDATION_PROMPT.format(
            article_text=article_text,
            grammar_point_name=grammar_name,
            grammar_point_description=grammar_description,
            detected_usage=self.format_detected_instances(detected_instances)
        )

        try:
            # 调用 Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # 解析响应
            response_text = response.content[0].text.strip()

            # 尝试提取 JSON
            validation_result = self._parse_validation_response(response_text)

            return validation_result

        except Exception as e:
            # 如果 API 调用失败，返回默认结果
            return {
                "is_correct": True,
                "confidence": 0.5,
                "issues": [f"API 调用失败: {str(e)}"],
                "missed_instances": [],
                "suggestions": []
            }

    def _parse_validation_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析 Claude 的验证响应

        Args:
            response_text: Claude 返回的文本

        Returns:
            解析后的验证结果
        """
        try:
            # 尝试查找 JSON 块
            # 可能的格式：```json\n{...}\n``` 或直接 {...}
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                result = json.loads(json_text)

                # 确保包含必需的字段
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
            # 如果解析失败，返回保守的默认值
            return {
                "is_correct": True,
                "confidence": 0.7,
                "issues": [f"响应解析失败: {str(e)}"],
                "missed_instances": [],
                "suggestions": []
            }

    async def validate_multiple_grammar_async(
        self,
        article_text: str,
        grammar_checks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量验证多个语法点

        Args:
            article_text: 文章文本
            grammar_checks: 语法检查列表
                [
                    {
                        "name": "把字句",
                        "description": "...",
                        "instances": [...]
                    },
                    ...
                ]

        Returns:
            验证结果列表
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


# 便捷函数
async def validate_grammar_with_claude(
    article_text: str,
    grammar_name: str,
    grammar_description: str,
    detected_instances: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：使用 Claude API 验证语法

    Args:
        article_text: 文章文本
        grammar_name: 语法点名称
        grammar_description: 语法点描述
        detected_instances: 检测到的实例
        api_key: API key（可选）

    Returns:
        验证结果
    """
    validator = ClaudeValidator(api_key)
    return await validator.validate_grammar_async(
        article_text,
        grammar_name,
        grammar_description,
        detected_instances
    )
