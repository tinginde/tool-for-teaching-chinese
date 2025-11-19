"""
语法点检测模块
使用正则表达式 + jieba 分词检测语法点，目标准确率：90%
"""
import re
from typing import List, Dict, Any, Optional

# jieba 是可选依赖，如果没有安装，分词功能将不可用
try:
    import jieba.posseg as pseg
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    pseg = None


class GrammarDetector:
    """语法点检测器 - 规则匹配 + 分词"""

    # 语法点的正则模式库
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

    # 语法点描述（用于 Claude 验证）
    GRAMMAR_DESCRIPTIONS = {
        "把字句": "处置式，表示对某事物进行处理或处置。基本结构：主语 + 把 + 宾语 + 动词 + 其他成分",
        "被动句": "被动语态，表示主语是动作的承受者。基本结构：主语 + 被 + (施事者) + 动词 + 其他成分",
        "比较句": "比较句式，用'比'表示两者之间的比较。基本结构：A + 比 + B + 形容词/副词",
        "使役句": "使役句式，表示让、叫、请别人做某事。基本结构：主语 + 让/叫/请 + 人 + 动词短语",
        "连动句": "连动句，一个主语连续做两个或多个动作。",
        "兼语句": "兼语句，一个成分既是前一动词的宾语，又是后一动词的主语。",
        "是...的": "强调句式，强调时间、地点、方式等。",
        "虽然...但是": "转折复句，表示转折关系。",
        "不但...而且": "递进复句，表示递进关系。",
        "因为...所以": "因果复句，表示因果关系。",
        "如果...就": "假设复句，表示假设条件。",
        "既...又": "并列复句，表示两种情况同时存在。",
        "一边...一边": "并列复句，表示两个动作同时进行。",
        "越...越": "递进复句，表示程度递增。",
    }

    def detect_grammar_pattern(self, article_text: str, grammar_name: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式检测语法点

        Args:
            article_text: 文章文本
            grammar_name: 语法点名称

        Returns:
            匹配结果列表
            [
                {
                    "text": "把垃圾放进垃圾桶",
                    "start": 12,
                    "end": 18,
                    "position": [12, 18]
                },
                ...
            ]
        """
        pattern = self.GRAMMAR_PATTERNS.get(grammar_name)
        if not pattern:
            # 如果没有预定义的模式，返回空列表
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
        使用 jieba 分词和词性标注辅助检测语法点

        Args:
            article_text: 文章文本
            grammar_name: 语法点名称

        Returns:
            检测结果列表
        """
        # 检查 jieba 是否可用
        if not JIEBA_AVAILABLE:
            # 如果 jieba 不可用，返回空列表
            return []

        # 分词并标注词性
        words = list(pseg.cut(article_text))

        matches = []

        # 根据不同语法点实现不同的检测逻辑
        if grammar_name == "把字句":
            matches = self._detect_ba_structure(article_text, words)
        elif grammar_name == "被动句":
            matches = self._detect_bei_structure(article_text, words)
        elif grammar_name == "比较句":
            matches = self._detect_bi_structure(article_text, words)

        return matches

    def _detect_ba_structure(
        self,
        text: str,
        words: List[tuple]
    ) -> List[Dict[str, Any]]:
        """
        检测把字句结构
        基本模式：把 + 名词 + 动词
        """
        matches = []
        text_position = 0

        for i, (word, pos) in enumerate(words):
            if word == "把" and i + 2 < len(words):
                # 检查后面是否有名词和动词
                next_word, next_pos = words[i + 1]
                next_next_word, next_next_pos = words[i + 2]

                if next_pos.startswith('n') and next_next_pos.startswith('v'):
                    # 找到把字句结构
                    start_pos = text.find(word, text_position)
                    # 估算结束位置（把 + 后续2-3个词）
                    phrase_length = len(word) + len(next_word) + len(next_next_word)
                    end_pos = start_pos + phrase_length + 5  # 加一些余量

                    # 提取实际文本
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
        """检测被动句结构"""
        matches = []
        text_position = 0

        for i, (word, pos) in enumerate(words):
            if word == "被" and i + 1 < len(words):
                start_pos = text.find(word, text_position)
                # 被动句通常包含被 + 若干词
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
        """检测比较句结构"""
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
        检测语法点（综合方法）

        Args:
            article_text: 文章文本
            grammar_name: 语法点名称
            use_segmentation: 是否使用分词辅助检测

        Returns:
            检测结果列表
        """
        # 优先使用正则表达式
        pattern_matches = self.detect_grammar_pattern(article_text, grammar_name)

        # 如果正则没有匹配到，且要求使用分词，则尝试分词方法
        if not pattern_matches and use_segmentation:
            return self.detect_grammar_by_segmentation(article_text, grammar_name)

        return pattern_matches

    def get_grammar_description(self, grammar_name: str) -> str:
        """获取语法点描述"""
        return self.GRAMMAR_DESCRIPTIONS.get(
            grammar_name,
            f"{grammar_name}：语法点描述"
        )

    def get_supported_grammar_points(self) -> List[str]:
        """获取支持的语法点列表"""
        return list(self.GRAMMAR_PATTERNS.keys())


# 便捷函数
def detect_grammar(
    article_text: str,
    grammar_name: str,
    use_segmentation: bool = False
) -> List[Dict[str, Any]]:
    """
    便捷函数：检测语法点

    Args:
        article_text: 文章文本
        grammar_name: 语法点名称
        use_segmentation: 是否使用分词辅助检测

    Returns:
        检测结果列表
    """
    detector = GrammarDetector()
    return detector.detect_grammar(article_text, grammar_name, use_segmentation)
