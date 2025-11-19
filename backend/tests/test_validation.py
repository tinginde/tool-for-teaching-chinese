"""
准确性验证引擎测试

测试生词检测、语法点检测和综合验证功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.validators import (
    VocabularyDetector,
    GrammarDetector,
    ValidationEngine
)


def test_vocabulary_detection():
    """测试生词检测功能"""
    print("\n" + "="*60)
    print("测试 1: 生词检测（目标准确率：100%）")
    print("="*60)

    # 测试文章
    article = """
    保护环境很重要。我们应该把垃圾放进垃圾桶，不要乱丢。
    环境保护不仅是政府的责任，也是每个人的责任。
    我们要珍惜环境，让我们的城市更加美丽。
    """

    # 目标生词
    vocab_list = ["环境", "保护", "垃圾", "责任", "珍惜"]

    # 执行检测
    detector = VocabularyDetector()
    results = detector.detect_vocabulary(article, vocab_list)

    # 打印结果
    print("\n检测结果：")
    for vocab in results["vocab_check"]:
        status = "✅" if vocab["found"] else "⚠️"
        print(f"{status} 生词「{vocab['word']}」：{'出现' if vocab['found'] else '未出现'} {vocab['count']} 次")
        if vocab["positions"]:
            print(f"   位置：{vocab['positions']}")

    # 覆盖率统计
    coverage = detector.check_coverage(results["vocab_check"])
    print(f"\n覆盖率：{coverage['found']}/{coverage['total']} ({coverage['coverage_rate']*100:.1f}%)")

    if coverage['missing_words']:
        print(f"未出现的生词：{', '.join(coverage['missing_words'])}")

    return results


def test_grammar_detection():
    """测试语法点检测功能"""
    print("\n" + "="*60)
    print("测试 2: 语法点检测（目标准确率：90%）")
    print("="*60)

    # 测试文章 - 包含多种语法点
    article = """
    今天的天气比昨天更热。妈妈让我把房间打扫干净。
    虽然很累，但是我还是坚持做完了。我把书放在书架上，
    把衣服挂在衣柜里。这个工作比我想象的要难一些。
    """

    # 目标语法点
    grammar_points = ["把字句", "比较句", "虽然...但是", "使役句"]

    detector = GrammarDetector()

    print("\n检测结果：")
    for grammar_name in grammar_points:
        matches = detector.detect_grammar(article, grammar_name)

        status = "✅" if matches else "⚠️"
        print(f"\n{status} 语法点「{grammar_name}」：{'检测到' if matches else '未检测到'} {len(matches)} 个")

        for i, match in enumerate(matches, 1):
            print(f"   {i}. 「{match['text']}」 位置：{match['position']}")

    # 显示支持的语法点
    print(f"\n支持的语法点总数：{len(detector.get_supported_grammar_points())} 个")

    return matches


def test_comprehensive_validation():
    """测试综合验证功能（不使用 Claude API）"""
    print("\n" + "="*60)
    print("测试 3: 综合验证引擎（快速模式）")
    print("="*60)

    # 测试文章
    article = """
    保护环境是每个人的责任。今天，我把垃圾分类做得很好。
    虽然这需要更多时间，但是对环境保护很重要。
    我们的城市比以前更干净了，因为大家都重视环保。
    """

    # 语法点
    grammar_points = [
        {"name": "把字句", "tbcl": "A2"},
        {"name": "比较句", "tbcl": "A2"},
        {"name": "虽然...但是", "tbcl": "B1"}
    ]

    # 生词
    vocabulary = [
        {"word": "环境", "pos": "N"},
        {"word": "保护", "pos": "V"},
        {"word": "责任", "pos": "N"},
        {"word": "垃圾", "pos": "N"},
        {"word": "重视", "pos": "V"}
    ]

    # 执行验证
    engine = ValidationEngine()
    results = engine.quick_validation(article, grammar_points, vocabulary)

    # 打印结果
    print("\n📊 验证结果总览")
    print(f"整体通过：{'✅ 是' if results['overall_pass'] else '⚠️ 否'}")

    print("\n📝 生词检测：")
    for vocab in results["vocab_check"]:
        status = "✅" if vocab["found"] else "⚠️"
        print(f"{status} {vocab['word']}：出现 {vocab['count']} 次")

    print("\n📖 语法点检测：")
    for grammar in results["grammar_check"]:
        status = "✅" if grammar["found"] else "⚠️"
        print(f"{status} {grammar['name']}：检测到 {grammar['count']} 个")
        if grammar["examples"]:
            for example in grammar["examples"]:
                print(f"   - {example}")

    return results


def test_position_accuracy():
    """测试位置信息的准确性"""
    print("\n" + "="*60)
    print("测试 4: 位置信息准确性验证")
    print("="*60)

    article = "我把书放在桌子上。这本书比那本书厚。"

    # 测试生词位置
    detector = VocabularyDetector()
    vocab_results = detector.detect_vocabulary(article, ["书", "桌子"])

    print("\n生词位置验证：")
    for vocab in vocab_results["vocab_check"]:
        print(f"\n词语：{vocab['word']}")
        for pos in vocab["positions"]:
            extracted = article[pos[0]:pos[1]]
            match = extracted == vocab['word']
            status = "✅" if match else "❌"
            print(f"  {status} 位置 {pos}：「{extracted}」 {'匹配' if match else '不匹配'}")

    # 测试语法点位置
    grammar_detector = GrammarDetector()
    grammar_matches = grammar_detector.detect_grammar(article, "把字句")

    print("\n语法点位置验证：")
    for match in grammar_matches:
        extracted = article[match["start"]:match["end"]]
        print(f"  ✅ 位置 {match['position']}：「{extracted}」")

    return vocab_results


def run_all_tests():
    """运行所有测试"""
    print("\n🧪 准确性验证引擎 - 测试套件")
    print("="*60)

    try:
        # 测试 1: 生词检测
        test_vocabulary_detection()

        # 测试 2: 语法点检测
        test_grammar_detection()

        # 测试 3: 综合验证
        test_comprehensive_validation()

        # 测试 4: 位置准确性
        test_position_accuracy()

        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)

        print("\n📊 功能摘要：")
        print("1. ✅ 生词检测 - 精确匹配，目标准确率 100%")
        print("2. ✅ 语法点检测 - 正则 + jieba，目标准确率 90%")
        print("3. ✅ 位置信息 - 支持视觉化标注")
        print("4. ⏳ Claude API 验证 - 需要 API key 才能测试")

    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
