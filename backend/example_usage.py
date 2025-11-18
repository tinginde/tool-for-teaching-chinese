"""
准确性验证引擎使用示例

展示如何使用验证引擎的各项功能
"""
from app.validators import (
    VocabularyDetector,
    GrammarDetector,
    ValidationEngine
)


def example_vocabulary_detection():
    """示例 1: 生词检测"""
    print("\n" + "="*60)
    print("示例 1: 生词检测")
    print("="*60)

    # 创建检测器
    detector = VocabularyDetector()

    # 教师输入的文章
    article = """
    保护环境是每个人的责任。我们应该节约用水，节约用电。
    环境保护不仅关系到我们自己，也关系到我们的下一代。
    让我们一起努力，保护我们的地球家园。
    """

    # 教师指定的生词
    vocabulary = ["环境", "保护", "责任", "节约", "下一代"]

    # 执行检测
    results = detector.detect_vocabulary(article, vocabulary)

    # 显示结果
    print(f"\n检测到 {len(results['vocab_check'])} 个生词：")
    for vocab in results['vocab_check']:
        status = "✅" if vocab['found'] else "❌"
        print(f"{status} {vocab['word']}: 出现 {vocab['count']} 次")

        # 显示每个出现的位置
        if vocab['positions']:
            for pos in vocab['positions']:
                context = article[max(0, pos[0]-5):min(len(article), pos[1]+5)]
                print(f"   位置 {pos}: ...{context.strip()}...")


def example_grammar_detection():
    """示例 2: 语法点检测"""
    print("\n" + "="*60)
    print("示例 2: 语法点检测")
    print("="*60)

    # 创建检测器
    detector = GrammarDetector()

    # 教师输入的文章
    article = """
    小明把作业做完了。虽然今天很累，但是他还是坚持学习。
    他的成绩比上个月更好了。因为他很努力，所以老师很高兴。
    """

    # 教师指定的语法点
    target_grammar = ["把字句", "比较句", "虽然...但是", "因为...所以"]

    # 显示支持的语法点总数
    all_grammar = detector.get_supported_grammar_points()
    print(f"\n系统支持 {len(all_grammar)} 个语法点")
    print(f"本次检测 {len(target_grammar)} 个语法点\n")

    # 检测每个语法点
    for grammar_name in target_grammar:
        matches = detector.detect_grammar(article, grammar_name)

        status = "✅" if matches else "❌"
        print(f"{status} {grammar_name}: 检测到 {len(matches)} 个")

        for i, match in enumerate(matches, 1):
            print(f"   {i}. 「{match['text']}」 位置: {match['position']}")


def example_quick_validation():
    """示例 3: 快速验证（教师实时编辑场景）"""
    print("\n" + "="*60)
    print("示例 3: 快速验证（实时编辑场景）")
    print("="*60)

    # 创建验证引擎
    engine = ValidationEngine()

    # 教师编辑的文章
    article = """
    今天是周末，小华把房间打扫得很干净。
    虽然打扫房间很累，但是看到干净的房间，她很开心。
    她的房间比以前更整洁了。
    """

    # 教学目标
    grammar_points = [
        {"name": "把字句", "tbcl": "A2"},
        {"name": "比较句", "tbcl": "A2"},
        {"name": "虽然...但是", "tbcl": "B1"}
    ]

    vocabulary = [
        {"word": "打扫", "pos": "V"},
        {"word": "整洁", "pos": "Adj"},
        {"word": "房间", "pos": "N"}
    ]

    # 快速验证（不使用 Claude API，适合实时场景）
    results = engine.quick_validation(article, grammar_points, vocabulary)

    # 显示验证结果
    print(f"\n整体评估: {'✅ 通过' if results['overall_pass'] else '❌ 不通过'}")

    print("\n生词检测:")
    for vocab in results['vocab_check']:
        status = "✅" if vocab['found'] else "❌"
        print(f"  {status} {vocab['word']}: {vocab['count']} 次")

    print("\n语法点检测:")
    for grammar in results['grammar_check']:
        status = "✅" if grammar['found'] else "❌"
        print(f"  {status} {grammar['name']}: {grammar['count']} 个")
        if grammar['examples']:
            for example in grammar['examples']:
                print(f"      - {example}")


def example_with_warnings():
    """示例 4: 带警告的验证（文章不完全符合要求）"""
    print("\n" + "="*60)
    print("示例 4: 验证不通过的情况")
    print("="*60)

    engine = ValidationEngine()

    # 不完整的文章（缺少某些语法点和生词）
    article = """
    保护环境很重要。我们应该节约资源。
    让我们一起努力，保护地球。
    """

    grammar_points = [
        {"name": "把字句", "tbcl": "A2"},      # 文章中没有
        {"name": "比较句", "tbcl": "A2"},      # 文章中没有
    ]

    vocabulary = [
        {"word": "环境", "pos": "N"},          # 有
        {"word": "保护", "pos": "V"},          # 有
        {"word": "责任", "pos": "N"},          # 没有
    ]

    results = engine.quick_validation(article, grammar_points, vocabulary)

    print(f"\n整体评估: {'✅ 通过' if results['overall_pass'] else '⚠️ 不通过'}")

    # 找出缺失的内容
    missing_vocab = [v['word'] for v in results['vocab_check'] if not v['found']]
    missing_grammar = [g['name'] for g in results['grammar_check'] if not g['found']]

    if missing_vocab:
        print(f"\n⚠️  缺少生词: {', '.join(missing_vocab)}")

    if missing_grammar:
        print(f"⚠️  缺少语法点: {', '.join(missing_grammar)}")

    print("\n💡 建议: 需要重新生成文章或手动编辑补充缺失的内容")


def main():
    """运行所有示例"""
    print("\n🎓 准确性验证引擎 - 使用示例")
    print("="*60)

    # 运行所有示例
    example_vocabulary_detection()
    example_grammar_detection()
    example_quick_validation()
    example_with_warnings()

    print("\n" + "="*60)
    print("✅ 所有示例运行完成！")
    print("="*60)

    print("\n📚 更多信息:")
    print("  - 查看 README.md 了解详细使用说明")
    print("  - 查看 tests/ 目录了解测试用例")
    print("  - 查看 claude.md 了解完整开发指引")


if __name__ == "__main__":
    main()
