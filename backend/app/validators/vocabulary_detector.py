"""
生词检测模块
使用精确字符串匹配检测生词，目标准确率：100%
"""
from typing import List, Dict, Any


class VocabularyDetector:
    """生词检测器 - 精确字符串匹配"""

    def detect_vocabulary(self, article_text: str, vocab_list: List[str]) -> Dict[str, Any]:
        """
        检测文章中的生词出现情况

        Args:
            article_text: 文章文本
            vocab_list: 生词列表

        Returns:
            检测结果，包含每个生词的出现次数和位置信息
            {
                "vocab_check": [
                    {
                        "word": "环境",
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
        找到词语在文本中所有出现的位置

        Args:
            text: 要搜索的文本
            word: 要查找的词语

        Returns:
            位置列表，每个位置是 [start, end] 格式
        """
        positions = []
        start = 0

        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            positions.append([pos, pos + len(word)])
            start = pos + 1  # 移动到下一个位置，处理重叠情况

        return positions

    def check_coverage(self, vocab_results: List[Dict]) -> Dict[str, Any]:
        """
        检查生词覆盖率

        Args:
            vocab_results: 生词检测结果列表

        Returns:
            覆盖率统计信息
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


# 便捷函数
def detect_vocabulary(article_text: str, vocab_list: List[str]) -> Dict[str, Any]:
    """
    便捷函数：检测文章中的生词

    Args:
        article_text: 文章文本
        vocab_list: 生词列表

    Returns:
        检测结果
    """
    detector = VocabularyDetector()
    return detector.detect_vocabulary(article_text, vocab_list)
