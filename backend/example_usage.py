"""
準確性驗證引擎使用示例

展示如何使用驗證引擎的各項功能
"""
from app.validators import (
    VocabularyDetector,
    GrammarDetector,
    ValidationEngine
)


def example_vocabulary_detection():
    """示例 1: 生詞檢測"""
    print("\n" + "="*60)
    print("示例 1: 生詞檢測")
    print("="*60)

    # 建立檢測器
    detector = VocabularyDetector()

    # 教師輸入的文章
    article = """
    保護環境是每個人的責任。我們應該節約用水，節約用電。
    環境保護不僅關係到我們自己，也關係到我們的下一代。
    讓我們一起努力，保護我們的地球家園。
    """

    # 教師指定的生詞
    vocabulary = ["環境", "保護", "責任", "節約", "下一代"]

    # 執行檢測
    results = detector.detect_vocabulary(article, vocabulary)

    # 顯示結果
    print(f"\n檢測到 {len(results['vocab_check'])} 個生詞：")
    for vocab in results['vocab_check']:
        status = "✅" if vocab['found'] else "❌"
        print(f"{status} {vocab['word']}: 出現 {vocab['count']} 次")

        # 顯示每個出現的位置
        if vocab['positions']:
            for pos in vocab['positions']:
                context = article[max(0, pos[0]-5):min(len(article), pos[1]+5)]
                print(f"   位置 {pos}: ...{context.strip()}...")


def example_grammar_detection():
    """示例 2: 語法點檢測"""
    print("\n" + "="*60)
    print("示例 2: 語法點檢測")
    print("="*60)

    # 建立檢測器
    detector = GrammarDetector()

    # 教師輸入的文章
    article = """
    小明把作業做完了。雖然今天很累，但是他還是堅持學習。
    他的成績比上個月更好了。因為他很努力，所以老師很高興。
    """

    # 教師指定的語法點
    target_grammar = ["把字句", "比較句", "雖然...但是", "因為...所以"]

    # 顯示支援的語法點總數
    all_grammar = detector.get_supported_grammar_points()
    print(f"\n系統支援 {len(all_grammar)} 個語法點")
    print(f"本次檢測 {len(target_grammar)} 個語法點\n")

    # 檢測每個語法點
    for grammar_name in target_grammar:
        matches = detector.detect_grammar(article, grammar_name)

        status = "✅" if matches else "❌"
        print(f"{status} {grammar_name}: 檢測到 {len(matches)} 個")

        for i, match in enumerate(matches, 1):
            print(f"   {i}. 「{match['text']}」 位置: {match['position']}")


def example_quick_validation():
    """示例 3: 快速驗證（教師即時編輯場景）"""
    print("\n" + "="*60)
    print("示例 3: 快速驗證（即時編輯場景）")
    print("="*60)

    # 建立驗證引擎
    engine = ValidationEngine()

    # 教師編輯的文章
    article = """
    今天是週末，小華把房間打掃得很乾淨。
    雖然打掃房間很累，但是看到乾淨的房間，她很開心。
    她的房間比以前更整潔了。
    """

    # 教學目標
    grammar_points = [
        {"name": "把字句", "tbcl": "A2"},
        {"name": "比較句", "tbcl": "A2"},
        {"name": "雖然...但是", "tbcl": "B1"}
    ]

    vocabulary = [
        {"word": "打掃", "pos": "V"},
        {"word": "整潔", "pos": "Adj"},
        {"word": "房間", "pos": "N"}
    ]

    # 快速驗證（不使用 Claude API，適合即時場景）
    results = engine.quick_validation(article, grammar_points, vocabulary)

    # 顯示驗證結果
    print(f"\n整體評估: {'✅ 通過' if results['overall_pass'] else '❌ 不通過'}")

    print("\n生詞檢測:")
    for vocab in results['vocab_check']:
        status = "✅" if vocab['found'] else "❌"
        print(f"  {status} {vocab['word']}: {vocab['count']} 次")

    print("\n語法點檢測:")
    for grammar in results['grammar_check']:
        status = "✅" if grammar['found'] else "❌"
        print(f"  {status} {grammar['name']}: {grammar['count']} 個")
        if grammar['examples']:
            for example in grammar['examples']:
                print(f"      - {example}")


def example_with_warnings():
    """示例 4: 帶警告的驗證（文章不完全符合要求）"""
    print("\n" + "="*60)
    print("示例 4: 驗證不通過的情況")
    print("="*60)

    engine = ValidationEngine()

    # 不完整的文章（缺少某些語法點和生詞）
    article = """
    保護環境很重要。我們應該節約資源。
    讓我們一起努力，保護地球。
    """

    grammar_points = [
        {"name": "把字句", "tbcl": "A2"},      # 文章中沒有
        {"name": "比較句", "tbcl": "A2"},      # 文章中沒有
    ]

    vocabulary = [
        {"word": "環境", "pos": "N"},          # 有
        {"word": "保護", "pos": "V"},          # 有
        {"word": "責任", "pos": "N"},          # 沒有
    ]

    results = engine.quick_validation(article, grammar_points, vocabulary)

    print(f"\n整體評估: {'✅ 通過' if results['overall_pass'] else '⚠️ 不通過'}")

    # 找出缺失的內容
    missing_vocab = [v['word'] for v in results['vocab_check'] if not v['found']]
    missing_grammar = [g['name'] for g in results['grammar_check'] if not g['found']]

    if missing_vocab:
        print(f"\n⚠️  缺少生詞: {', '.join(missing_vocab)}")

    if missing_grammar:
        print(f"⚠️  缺少語法點: {', '.join(missing_grammar)}")

    print("\n💡 建議: 需要重新生成文章或手動編輯補充缺失的內容")


def main():
    """運行所有示例"""
    print("\n🎓 準確性驗證引擎 - 使用示例")
    print("="*60)

    # 運行所有示例
    example_vocabulary_detection()
    example_grammar_detection()
    example_quick_validation()
    example_with_warnings()

    print("\n" + "="*60)
    print("✅ 所有示例運行完成！")
    print("="*60)

    print("\n📚 更多資訊:")
    print("  - 查看 README.md 了解詳細使用說明")
    print("  - 查看 tests/ 目錄了解測試用例")
    print("  - 查看 claude.md 了解完整開發指引")


if __name__ == "__main__":
    main()
