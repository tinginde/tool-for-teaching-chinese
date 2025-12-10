"""
語法點檢測模組
使用正則表達式 + jieba 分詞檢測語法點，目標準確率：90%
"""
import re
from typing import List, Dict, Any, Optional

# jieba 是可選依賴，如果沒有安裝，分詞功能將不可用
try:
    import jieba.posseg as pseg
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    pseg = None


class GrammarDetector:
    """語法點檢測器 - 規則匹配 + 分詞"""

    # 語法點的正則模式庫
    GRAMMAR_PATTERNS = {
        "把字句": r"把[\u4e00-\u9fa5]{1,10}[给]?[\u4e00-\u9fa5]{1,10}",
        "被动句": r"被[\u4e00-\u9fa5]{1,10}[了]?",
        "比较句": r"比[\u4e00-\u9fa5]{1,10}[更还]?[\u4e00-\u9fa5]{1,5}",
        "使役句": r"[让叫请][\u4e00-\u9fa5]{1,5}[\u4e00-\u9fa5]{1,10}",
        "连动句": r"[\u4e00-\u9fa5]{1,5}去[\u4e00-\u9fa5]{1,5}",
        "兼语句": r"[请让叫][\u4e00-\u9fa5]{1,5}[来去][\u4e00-\u9fa5]{1,10}",
        "是...的": r"是[\u4e00-\u9fa5]{1,20}的",
        "虽然...但是": r"虽然[\u4e00-\u9fa5，。！？]{1,50}但是",
        "不但...而且": r"不但[\u4e00-\u9fa5，。！？]{1,50}而且",
        "因为...所以": r"因为[\u4e00-\u9fa5，。！？]{1,50}所以",
        "如果...就": r"如果[\u4e00-\u9fa5，。！？]{1,50}就",
        "既...又": r"既[\u4e00-\u9fa5]{1,10}又[\u4e00-\u9fa5]{1,10}",
        "一边...一边": r"一边[\u4e00-\u9fa5]{1,10}一边[\u4e00-\u9fa5]{1,10}",
        "越...越": r"越[\u4e00-\u9fa5]{1,10}越[\u4e00-\u9fa5]{1,10}",
        "不仅...还": r"不仅[\u4e00-\u9fa5，。！？]{1,50}还",
        "无论...都": r"无论[\u4e00-\u9fa5，。！？]{1,50}都",
        "只要...就": r"只要[\u4e00-\u9fa5，。！？]{1,50}就",
        "除了...以外": r"除了[\u4e00-\u9fa5]{1,20}以外",
        "不是...而是": r"不是[\u4e00-\u9fa5]{1,20}而是",
        "与其...不如": r"与其[\u4e00-\u9fa5，。！？]{1,50}不如",
        "宁可...也": r"宁可[\u4e00-\u9fa5，。！？]{1,50}也",
        "就算...也": r"就算[\u4e00-\u9fa5，。！？]{1,50}也",
        "哪怕...也": r"哪怕[\u4e00-\u9fa5，。！？]{1,50}也",
        "只有...才": r"只有[\u4e00-\u9fa5，。！？]{1,50}才",
        "凡是...都": r"凡是[\u4e00-\u9fa5，。！？]{1,50}都",
        "既然...就": r"既然[\u4e00-\u9fa5，。！？]{1,50}就",
        "由于...因此": r"由于[\u4e00-\u9fa5，。！？]{1,50}因此",
        "尽管...还是": r"尽管[\u4e00-\u9fa5，。！？]{1,50}还是",
        "即使...也": r"即使[\u4e00-\u9fa5，。！？]{1,50}也",
        "不管...都": r"不管[\u4e00-\u9fa5，。！？]{1,50}都",
    }

    # 語法點描述（用於 Claude 驗證）
    GRAMMAR_DESCRIPTIONS = {
        "把字句": "處置式，表示對某事物進行處理或處置。基本結構：主語 + 把 + 賓語 + 動詞 + 其他成分",
        "被動句": "被動語態，表示主語是動作的承受者。基本結構：主語 + 被 + (施事者) + 動詞 + 其他成分",
        "比較句": "比較句式，用'比'表示兩者之間的比較。基本結構：A + 比 + B + 形容詞/副詞",
        "使役句": "使役句式，表示讓、叫、請別人做某事。基本結構：主語 + 讓/叫/請 + 人 + 動詞短語",
        "連動句": "連動句，一個主語連續做兩個或多個動作。",
        "兼語句": "兼語句，一個成分既是前一動詞的賓語，又是後一動詞的主語。",
        "是...的": "強調句式，強調時間、地點、方式等。",
        "雖然...但是": "轉折複句，表示轉折關係。",
        "不但...而且": "遞進複句，表示遞進關係。",
        "因為...所以": "因果複句，表示因果關係。",
        "如果...就": "假設複句，表示假設條件。",
        "既...又": "並列複句，表示兩種情況同時存在。",
        "一邊...一邊": "並列複句，表示兩個動作同時進行。",
        "越...越": "遞進複句，表示程度遞增。",
    }

    def detect_grammar_pattern(self, article_text: str, grammar_name: str) -> List[Dict[str, Any]]:
        """
        使用正則表達式檢測語法點

        Args:
            article_text: 文章文本
            grammar_name: 語法點名稱

        Returns:
            匹配結果列表
            [
                {
                    "text": "把垃圾放進垃圾桶",
                    "start": 12,
                    "end": 18,
                    "position": [12, 18]
                },
                ...
            ]
        """
        pattern = self.GRAMMAR_PATTERNS.get(grammar_name)
        if not pattern:
            # 如果沒有預定義的模式，返回空列表
            return []

        matches = []
        for match in re.finditer(pattern, article_text):
            matches.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "position": [match.start(), match.end()]
            })

        return matches

    def detect_grammar_by_segmentation(
        self,
        article_text: str,
        grammar_name: str
    ) -> List[Dict[str, Any]]:
        """
        使用 jieba 分詞和詞性標注輔助檢測語法點

        Args:
            article_text: 文章文本
            grammar_name: 語法點名稱

        Returns:
            檢測結果列表
        """
        # 檢查 jieba 是否可用
        if not JIEBA_AVAILABLE:
            # 如果 jieba 不可用，返回空列表
            return []

        # 分詞並標注詞性
        words = list(pseg.cut(article_text))

        matches = []

        # 根據不同語法點實現不同的檢測邏輯
        if grammar_name == "把字句":
            matches = self._detect_ba_structure(article_text, words)
        elif grammar_name == "被動句":
            matches = self._detect_bei_structure(article_text, words)
        elif grammar_name == "比較句":
            matches = self._detect_bi_structure(article_text, words)

        return matches

    def _detect_ba_structure(
        self,
        text: str,
        words: List[tuple]
    ) -> List[Dict[str, Any]]:
        """
        檢測把字句結構
        基本模式：把 + 名詞 + 動詞
        """
        matches = []
        text_position = 0

        for i, (word, pos) in enumerate(words):
            if word == "把" and i + 2 < len(words):
                # 檢查後面是否有名詞和動詞
                next_word, next_pos = words[i + 1]
                next_next_word, next_next_pos = words[i + 2]

                if next_pos.startswith('n') and next_next_pos.startswith('v'):
                    # 找到把字句結構
                    start_pos = text.find(word, text_position)
                    # 估算結束位置（把 + 後續2-3個詞）
                    phrase_length = len(word) + len(next_word) + len(next_next_word)
                    end_pos = start_pos + phrase_length + 5  # 加一些餘量

                    # 提取實際文本
                    phrase = text[start_pos:min(end_pos, len(text))]

                    matches.append({
                        "text": phrase,
                        "start": start_pos,
                        "end": min(end_pos, len(text)),
                        "position": [start_pos, min(end_pos, len(text))]
                    })

            text_position += len(word)

        return matches

    def _detect_bei_structure(
        self,
        text: str,
        words: List[tuple]
    ) -> List[Dict[str, Any]]:
        """檢測被動句結構"""
        matches = []
        text_position = 0

        for i, (word, pos) in enumerate(words):
            if word == "被" and i + 1 < len(words):
                start_pos = text.find(word, text_position)
                # 被動句通常包含被 + 若干詞
                end_estimate = start_pos + 20
                phrase = text[start_pos:min(end_estimate, len(text))]

                matches.append({
                    "text": phrase,
                    "start": start_pos,
                    "end": min(end_estimate, len(text)),
                    "position": [start_pos, min(end_estimate, len(text))]
                })

            text_position += len(word)

        return matches

    def _detect_bi_structure(
        self,
        text: str,
        words: List[tuple]
    ) -> List[Dict[str, Any]]:
        """檢測比較句結構"""
        matches = []
        text_position = 0

        for i, (word, pos) in enumerate(words):
            if word == "比" and i + 1 < len(words):
                start_pos = text.find(word, text_position)
                end_estimate = start_pos + 15
                phrase = text[start_pos:min(end_estimate, len(text))]

                matches.append({
                    "text": phrase,
                    "start": start_pos,
                    "end": min(end_estimate, len(text)),
                    "position": [start_pos, min(end_estimate, len(text))]
                })

            text_position += len(word)

        return matches

    def detect_grammar(
        self,
        article_text: str,
        grammar_name: str,
        use_segmentation: bool = False
    ) -> List[Dict[str, Any]]:
        """
        檢測語法點（綜合方法）

        Args:
            article_text: 文章文本
            grammar_name: 語法點名稱
            use_segmentation: 是否使用分詞輔助檢測

        Returns:
            檢測結果列表
        """
        # 優先使用正則表達式
        pattern_matches = self.detect_grammar_pattern(article_text, grammar_name)

        # 如果正則沒有匹配到，且要求使用分詞，則嘗試分詞方法
        if not pattern_matches and use_segmentation:
            return self.detect_grammar_by_segmentation(article_text, grammar_name)

        return pattern_matches

    def get_grammar_description(self, grammar_name: str) -> str:
        """獲取語法點描述"""
        return self.GRAMMAR_DESCRIPTIONS.get(
            grammar_name,
            f"{grammar_name}：語法點描述"
        )

    def get_supported_grammar_points(self) -> List[str]:
        """獲取支持的語法點列表"""
        return list(self.GRAMMAR_PATTERNS.keys())


# 便捷函數
def detect_grammar(
    article_text: str,
    grammar_name: str,
    use_segmentation: bool = False
) -> List[Dict[str, Any]]:
    """
    便捷函數：檢測語法點

    Args:
        article_text: 文章文本
        grammar_name: 語法點名稱
        use_segmentation: 是否使用分詞輔助檢測

    Returns:
        檢測結果列表
    """
    detector = GrammarDetector()
    return detector.detect_grammar(article_text, grammar_name, use_segmentation)
