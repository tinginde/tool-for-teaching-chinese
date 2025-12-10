"""
生詞檢測模組
使用精確字符串匹配檢測生詞，目標準確率：100%
"""
from typing import List, Dict, Any


class VocabularyDetector:
    """生詞檢測器 - 精確字符串匹配"""

    def detect_vocabulary(self, article_text: str, vocab_list: List[str]) -> Dict[str, Any]:
        """
        檢測文章中的生詞出現情況

        Args:
            article_text: 文章文本
            vocab_list: 生詞列表

        Returns:
            檢測結果，包含每個生詞的出現次數和位置信息
            {
                "vocab_check": [
                    {
                        "word": "環境",
                        "found": True,
                        "count": 3,
                        "positions": [[23, 25], [67, 69], [102, 104]]
                    },
                    ...
                ]
            }
        """
        results = []

        for word in vocab_list:
            positions = self._find_all_positions(article_text, word)

            results.append({
                "word": word,
                "found": len(positions) > 0,
                "count": len(positions),
                "positions": positions
            })

        return {"vocab_check": results}

    def _find_all_positions(self, text: str, word: str) -> List[List[int]]:
        """
        找到詞語在文本中所有出現的位置

        Args:
            text: 要搜索的文本
            word: 要查找的詞語

        Returns:
            位置列表，每個位置是 [start, end] 格式
        """
        positions = []
        start = 0

        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            positions.append([pos, pos + len(word)])
            start = pos + 1  # 移動到下一個位置，處理重疊情況

        return positions

    def check_coverage(self, vocab_results: List[Dict]) -> Dict[str, Any]:
        """
        檢查生詞覆蓋率

        Args:
            vocab_results: 生詞檢測結果列表

        Returns:
            覆蓋率統計信息
        """
        total_words = len(vocab_results)
        found_words = sum(1 for v in vocab_results if v["found"])
        missing_words = [v["word"] for v in vocab_results if not v["found"]]

        return {
            "total": total_words,
            "found": found_words,
            "missing": len(missing_words),
            "coverage_rate": found_words / total_words if total_words > 0 else 0,
            "missing_words": missing_words
        }


# 便捷函數
def detect_vocabulary(article_text: str, vocab_list: List[str]) -> Dict[str, Any]:
    """
    便捷函數：檢測文章中的生詞

    Args:
        article_text: 文章文本
        vocab_list: 生詞列表

    Returns:
        檢測結果
    """
    detector = VocabularyDetector()
    return detector.detect_vocabulary(article_text, vocab_list)
