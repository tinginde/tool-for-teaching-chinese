"""
準確性驗證引擎測試

測試生詞檢測、語法點檢測和綜合驗證功能
"""
import sys
import os

# 添加項目路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.validators import (
    VocabularyDetector,
    GrammarDetector,
    ValidationEngine
)


def test_vocabulary_detection():
    """測試生詞檢測功能"""
    print("\n" + "="*60)
    print("測試 1: 生詞檢測（目標準確率：100%）")
    print("="*60)

    # 測試文章
    article = """
    保護環境很重要。我們應該把垃圾放進垃圾桶，不要亂丟。
    環境保護不僅是政府的責任，也是每個人的責任。
    我們要珍惜環境，讓我們的城市更加美麗。
    """

    # 目標生詞
    vocab_list = ["環境", "保護", "垃圾", "責任", "珍惜"]

    # 執行檢測
    detector = VocabularyDetector()
    results = detector.detect_vocabulary(article, vocab_list)

    # 打印結果
    print("\n檢測結果：")
    for vocab in results["vocab_check"]:
        status = "✅" if vocab["found"] else "⚠️"
        print(f"{status} 生詞「{vocab['word']}」：{'出現' if vocab['found'] else '未出現'} {vocab['count']} 次")
        if vocab["positions"]:
            print(f"   位置：{vocab['positions']}")

    # 覆蓋率統計
    coverage = detector.check_coverage(results["vocab_check"])
    print(f"\n覆蓋率：{coverage['found']}/{coverage['total']} ({coverage['coverage_rate']*100:.1f}%)")

    if coverage['missing_words']:
        print(f"未出現的生詞：{', '.join(coverage['missing_words'])}")

    return results


def test_grammar_detection():
    """測試語法點檢測功能"""
    print("\n" + "="*60)
    print("測試 2: 語法點檢測（目標準確率：90%）")
    print("="*60)

    # 測試文章 - 包含多種語法點
    article = """
    今天的天氣比昨天更熱。媽媽讓我把房間打掃乾淨。
    雖然很累，但是我還是堅持做完了。我把書放在書架上，
    把衣服掛在衣櫃裡。這個工作比我想像的要難一些。
    """

    # 目標語法點
    grammar_points = ["把字句", "比較句", "雖然...但是", "使役句"]

    detector = GrammarDetector()

    print("\n檢測結果：")
    for grammar_name in grammar_points:
        matches = detector.detect_grammar(article, grammar_name)

        status = "✅" if matches else "⚠️"
        print(f"\n{status} 語法點「{grammar_name}」：{'檢測到' if matches else '未檢測到'} {len(matches)} 個")

        for i, match in enumerate(matches, 1):
            print(f"   {i}. 「{match['text']}」 位置：{match['position']}")

    # 顯示支援的語法點
    print(f"\n支援的語法點總數：{len(detector.get_supported_grammar_points())} 個")

    return matches


def test_comprehensive_validation():
    """測試綜合驗證功能（不使用 Claude API）"""
    print("\n" + "="*60)
    print("測試 3: 綜合驗證引擎（快速模式）")
    print("="*60)

    # 測試文章
    article = """
    保護環境是每個人的責任。今天，我把垃圾分類做得很好。
    雖然這需要更多時間，但是對環境保護很重要。
    我們的城市比以前更乾淨了，因為大家都重視環保。
    """

    # 語法點
    grammar_points = [
        {"name": "把字句", "tbcl": "A2"},
        {"name": "比較句", "tbcl": "A2"},
        {"name": "雖然...但是", "tbcl": "B1"}
    ]

    # 生詞
    vocabulary = [
        {"word": "環境", "pos": "N"},
        {"word": "保護", "pos": "V"},
        {"word": "責任", "pos": "N"},
        {"word": "垃圾", "pos": "N"},
        {"word": "重視", "pos": "V"}
    ]

    # 執行驗證
    engine = ValidationEngine()
    results = engine.quick_validation(article, grammar_points, vocabulary)

    # 打印結果
    print("\n📊 驗證結果總覽")
    print(f"整體通過：{'✅ 是' if results['overall_pass'] else '⚠️ 否'}")

    print("\n📝 生詞檢測：")
    for vocab in results["vocab_check"]:
        status = "✅" if vocab["found"] else "⚠️"
        print(f"{status} {vocab['word']}：出現 {vocab['count']} 次")

    print("\n📖 語法點檢測：")
    for grammar in results["grammar_check"]:
        status = "✅" if grammar["found"] else "⚠️"
        print(f"{status} {grammar['name']}：檢測到 {grammar['count']} 個")
        if grammar["examples"]:
            for example in grammar["examples"]:
                print(f"   - {example}")

    return results


def test_position_accuracy():
    """測試位置資訊的準確性"""
    print("\n" + "="*60)
    print("測試 4: 位置資訊準確性驗證")
    print("="*60)

    article = "我把書放在桌子上。這本書比那本書厚。"

    # 測試生詞位置
    detector = VocabularyDetector()
    vocab_results = detector.detect_vocabulary(article, ["書", "桌子"])

    print("\n生詞位置驗證：")
    for vocab in vocab_results["vocab_check"]:
        print(f"\n詞語：{vocab['word']}")
        for pos in vocab["positions"]:
            extracted = article[pos[0]:pos[1]]
            match = extracted == vocab['word']
            status = "✅" if match else "❌"
            print(f"  {status} 位置 {pos}：「{extracted}」 {'匹配' if match else '不匹配'}")

    # 測試語法點位置
    grammar_detector = GrammarDetector()
    grammar_matches = grammar_detector.detect_grammar(article, "把字句")

    print("\n語法點位置驗證：")
    for match in grammar_matches:
        extracted = article[match["start"]:match["end"]]
        print(f"  ✅ 位置 {match['position']}：「{extracted}」")

    return vocab_results


def run_all_tests():
    """運行所有測試"""
    print("\n🧪 準確性驗證引擎 - 測試套件")
    print("="*60)

    try:
        # 測試 1: 生詞檢測
        test_vocabulary_detection()

        # 測試 2: 語法點檢測
        test_grammar_detection()

        # 測試 3: 綜合驗證
        test_comprehensive_validation()

        # 測試 4: 位置準確性
        test_position_accuracy()

        print("\n" + "="*60)
        print("✅ 所有測試完成！")
        print("="*60)

        print("\n📊 功能摘要：")
        print("1. ✅ 生詞檢測 - 精確匹配，目標準確率 100%")
        print("2. ✅ 語法點檢測 - 正則 + jieba，目標準確率 90%")
        print("3. ✅ 位置資訊 - 支援視覺化標註")
        print("4. ⏳ Claude API 驗證 - 需要 API key 才能測試")

    except Exception as e:
        print(f"\n❌ 測試失敗：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
