"""
Example API client for the Chinese Teaching Tool.

This script demonstrates how to use the FastAPI backend.
"""

import requests
import json
import sys


# API base URL
BASE_URL = "http://localhost:8000/api/v1"


def generate_article():
    """Generate an article."""
    print("\n" + "=" * 60)
    print("📝 Step 1: Generate Article")
    print("=" * 60)

    url = f"{BASE_URL}/generate/article"
    payload = {
        "grammar_points": [
            {"name": "把字句", "tbcl_level": "A2"},
            {"name": "比較句", "tbcl_level": "A2"}
        ],
        "vocabulary": [
            {"word": "環境", "pos": "N"},
            {"word": "保護", "pos": "V"},
            {"word": "垃圾", "pos": "N"},
            {"word": "責任", "pos": "N"},
            {"word": "珍惜", "pos": "V"}
        ],
        "article_type": "daily_life",
        "tbcl_level": "A2",
        "length": 400,
        "topic": "環保生活",
        "auto_validate": True
    }

    print("\n📤 Sending request...")
    print(f"語法點: {', '.join([g['name'] for g in payload['grammar_points']])}")
    print(f"生詞: {', '.join([v['word'] for v in payload['vocabulary']])}")
    print(f"主題: {payload['topic']}")

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 文章生成成功！")
            print(f"   字數：{result['word_count']}")
            print(f"   生成時間：{result['generation_time']:.2f}秒")
            print(f"   文章ID：{result['article_id']}")

            if result.get('validation_result'):
                val = result['validation_result']
                print(f"\n📊 自動驗證結果：")
                print(f"   整體通過：{'✅' if val['overall_pass'] else '❌'}")
                print(f"   語法檢測：{len(val['grammar_check'])} 個語法點")
                print(f"   生詞檢測：{len(val['vocab_check'])} 個生詞")

            print(f"\n📄 文章內容：")
            print("-" * 60)
            print(result['article_text'])
            print("-" * 60)

            return result

        else:
            error = response.json()
            print(f"\n❌ 錯誤 {response.status_code}: {error.get('detail', 'Unknown error')}")
            return None

    except requests.exceptions.Timeout:
        print("\n❌ 請求超時。請確保：")
        print("   1. 服務器正在運行")
        print("   2. ANTHROPIC_API_KEY 已設置")
        return None
    except requests.exceptions.ConnectionError:
        print("\n❌ 無法連接到服務器。請確保服務器正在運行：")
        print("   python3 -m uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ 發生錯誤：{str(e)}")
        return None


def validate_article(article_text):
    """Validate an article."""
    print("\n" + "=" * 60)
    print("✅ Step 2: Validate Article")
    print("=" * 60)

    url = f"{BASE_URL}/validate/"
    payload = {
        "article_text": article_text,
        "grammar_points": [
            {"name": "把字句"},
            {"name": "比較句"}
        ],
        "vocabulary": [
            {"word": "環境"},
            {"word": "保護"},
            {"word": "垃圾"}
        ],
        "use_claude_validation": False  # Set to True to use Claude API validation
    }

    print("\n📤 Sending validation request...")

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 驗證完成！")
            print(f"   整體通過：{'✅ 是' if result['overall_pass'] else '❌ 否'}")
            print(f"   驗證時間：{result['validation_time']:.2f}秒")

            # Grammar check results
            print(f"\n📊 語法點檢測：")
            for g in result['grammar_check']:
                status = "✅" if g['found'] else "❌"
                print(f"   {status} {g['name']}: 出現 {g['count']} 次")
                if g.get('examples'):
                    print(f"      示例: {', '.join(g['examples'][:2])}")

            # Vocabulary check results
            print(f"\n📊 生詞檢測：")
            for v in result['vocab_check']:
                status = "✅" if v['found'] else "❌"
                print(f"   {status} {v['word']}: 出現 {v['count']} 次")

            # Warnings
            if result.get('warnings'):
                print(f"\n⚠️ 警告：")
                for w in result['warnings']:
                    print(f"   - {w}")

            # Statistics
            stats = result.get('statistics', {})
            if stats:
                print(f"\n📈 統計：")
                print(f"   語法通過率：{stats.get('grammar_pass_rate', 0):.0%}")
                print(f"   生詞通過率：{stats.get('vocab_pass_rate', 0):.0%}")

            return result

        else:
            error = response.json()
            print(f"\n❌ 錯誤 {response.status_code}: {error.get('detail', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"\n❌ 發生錯誤：{str(e)}")
        return None


def generate_questions(article_text):
    """Generate questions based on an article."""
    print("\n" + "=" * 60)
    print("❓ Step 3: Generate Questions")
    print("=" * 60)

    url = f"{BASE_URL}/generate/questions"
    payload = {
        "article_text": article_text,
        "num_questions": 3,
        "question_types": ["multiple_choice"],
        "focus_areas": ["comprehension", "vocabulary"]
    }

    print("\n📤 Sending request to generate questions...")

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 題目生成成功！")
            print(f"   題目數量：{len(result['questions'])}")
            print(f"   生成時間：{result['generation_time']:.2f}秒")

            print(f"\n📝 題目列表：")
            print("-" * 60)
            for i, q in enumerate(result['questions'], 1):
                print(f"\n{i}. {q['question_text']}")
                if q.get('options'):
                    for j, opt in enumerate(q['options'], 1):
                        label = chr(64 + j)  # A, B, C, D
                        print(f"   {label}. {opt}")
                print(f"\n   ✓ 正確答案：{q['correct_answer']}")
                if q.get('explanation'):
                    print(f"   💡 解析：{q['explanation']}")

            print("-" * 60)

            return result

        else:
            error = response.json()
            print(f"\n❌ 錯誤 {response.status_code}: {error.get('detail', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"\n❌ 發生錯誤：{str(e)}")
        return None


def export_content(article_text, questions=None):
    """Export content to HTML."""
    print("\n" + "=" * 60)
    print("💾 Step 4: Export Content")
    print("=" * 60)

    url = f"{BASE_URL}/export/"
    payload = {
        "article_text": article_text,
        "questions": questions,
        "format": "html",
        "include_answers": True,
        "include_validation": False,
        "title": "華語閱讀理解練習"
    }

    print("\n📤 Sending export request...")

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 匯出成功！")
            print(f"   格式：{result['format'].upper()}")
            print(f"   檔案名：{result['filename']}")
            print(f"   大小：{result['size_bytes']} bytes")

            # Save to file
            filename = result['filename']
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result['content'])

            print(f"\n💾 已保存到：{filename}")
            print(f"   可以在瀏覽器中打開查看")

            return result

        else:
            error = response.json()
            print(f"\n❌ 錯誤 {response.status_code}: {error.get('detail', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"\n❌ 發生錯誤：{str(e)}")
        return None


def main():
    """Main workflow."""
    print("\n" + "=" * 60)
    print("🚀 華語教材智能生成器 - API 客戶端示例")
    print("=" * 60)
    print("\n此腳本將演示完整的工作流程：")
    print("  1. 生成文章")
    print("  2. 驗證文章")
    print("  3. 生成題目")
    print("  4. 匯出內容")
    print("\n請確保 API 服務器正在運行：")
    print("  python3 -m uvicorn app.main:app --reload")
    print()

    input("按 Enter 鍵開始... ")

    # Step 1: Generate article
    article_result = generate_article()
    if not article_result:
        print("\n❌ 文章生成失敗，流程終止。")
        return

    article_text = article_result['article_text']

    # Step 2: Validate article
    validate_article(article_text)

    # Step 3: Generate questions
    questions_result = generate_questions(article_text)

    # Step 4: Export
    if questions_result:
        questions = [q.dict() if hasattr(q, 'dict') else q for q in questions_result['questions']]
        export_content(article_text, questions)

    print("\n" + "=" * 60)
    print("✅ 完成！所有步驟都已執行。")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 發生未預期的錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
