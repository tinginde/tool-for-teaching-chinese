"""
Export service for generating various output formats.
"""

import json
from typing import List, Optional, Dict
from datetime import datetime

from ..schemas.export import ExportFormat


class ExportService:
    """Service for exporting content to various formats."""

    def export_to_html(
        self,
        article_text: str,
        questions: Optional[List[Dict]] = None,
        validation_result: Optional[Dict] = None,
        include_answers: bool = True,
        include_validation: bool = False,
        title: Optional[str] = None,
    ) -> str:
        """
        Export content to HTML format.

        Args:
            article_text: The article text
            questions: Optional list of questions
            validation_result: Optional validation result
            include_answers: Whether to include answers
            include_validation: Whether to include validation report
            title: Document title

        Returns:
            HTML string
        """
        doc_title = title or "華語閱讀理解練習"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_title}</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', 'PingFang TC', sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.8;
            color: #333;
        }}
        h1 {{
            color: #2c5282;
            border-bottom: 3px solid #4299e1;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2d3748;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .article {{
            background-color: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .question {{
            margin: 20px 0;
            padding: 15px;
            background-color: #fff;
            border-left: 4px solid #4299e1;
        }}
        .options {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .option {{
            margin: 5px 0;
        }}
        .answer {{
            color: #38a169;
            font-weight: bold;
            margin-top: 10px;
        }}
        .explanation {{
            color: #666;
            font-style: italic;
            margin-top: 5px;
        }}
        .validation {{
            background-color: #fffaf0;
            border: 1px solid #f6ad55;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}
        .timestamp {{
            color: #718096;
            font-size: 0.9em;
            text-align: right;
            margin-top: 30px;
        }}
        .print-hide {{
            display: block;
        }}
        @media print {{
            .print-hide {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <h1>{doc_title}</h1>

    <h2>📖 文章</h2>
    <div class="article">
        {self._format_text_to_html(article_text)}
    </div>
"""

        # Add questions if provided
        if questions:
            html += """
    <h2>📝 閱讀理解題目</h2>
"""
            for i, q in enumerate(questions, 1):
                html += f"""
    <div class="question">
        <strong>{i}. {q.get('question_text', '')}</strong>
"""
                if q.get('options'):
                    html += """
        <div class="options">
"""
                    for j, option in enumerate(q['options'], 1):
                        label = chr(64 + j)  # A, B, C, D
                        html += f"""
            <div class="option">{label}. {option}</div>
"""
                    html += """
        </div>
"""

                if include_answers:
                    html += f"""
        <div class="answer">✓ 正確答案：{q.get('correct_answer', '')}</div>
"""
                    if q.get('explanation'):
                        html += f"""
        <div class="explanation">解析：{q['explanation']}</div>
"""

                html += """
    </div>
"""

        # Add validation result if provided and requested
        if include_validation and validation_result:
            html += """
    <h2>✅ 驗證報告</h2>
    <div class="validation">
"""
            if validation_result.get('overall_pass'):
                html += """
        <p><strong>整體評估：✅ 通過</strong></p>
"""
            else:
                html += """
        <p><strong>整體評估：⚠️ 未通過</strong></p>
"""

            # Grammar check results
            if validation_result.get('grammar_check'):
                html += """
        <h3>語法點檢測</h3>
        <ul>
"""
                for g in validation_result['grammar_check']:
                    status = "✅" if g.get('found') else "❌"
                    html += f"""
            <li>{status} {g.get('name')}：出現 {g.get('count', 0)} 次</li>
"""
                html += """
        </ul>
"""

            # Vocabulary check results
            if validation_result.get('vocab_check'):
                html += """
        <h3>生詞檢測</h3>
        <ul>
"""
                for v in validation_result['vocab_check']:
                    status = "✅" if v.get('found') else "❌"
                    html += f"""
            <li>{status} {v.get('word')}：出現 {v.get('count', 0)} 次</li>
"""
                html += """
        </ul>
"""

            html += """
    </div>
"""

        # Footer
        html += f"""
    <div class="timestamp">
        生成時間：{timestamp}
    </div>
</body>
</html>
"""
        return html

    def export_to_txt(
        self,
        article_text: str,
        questions: Optional[List[Dict]] = None,
        include_answers: bool = True,
        title: Optional[str] = None,
    ) -> str:
        """
        Export content to plain text format.

        Args:
            article_text: The article text
            questions: Optional list of questions
            include_answers: Whether to include answers
            title: Document title

        Returns:
            Plain text string
        """
        doc_title = title or "華語閱讀理解練習"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        txt = f"{doc_title}\n{'=' * len(doc_title)}\n\n"
        txt += f"【文章】\n\n{article_text}\n\n"

        if questions:
            txt += f"\n{'=' * 50}\n"
            txt += "【閱讀理解題目】\n\n"

            for i, q in enumerate(questions, 1):
                txt += f"{i}. {q.get('question_text', '')}\n"

                if q.get('options'):
                    for j, option in enumerate(q['options'], 1):
                        label = chr(64 + j)
                        txt += f"   {label}. {option}\n"

                if include_answers:
                    txt += f"\n   ✓ 正確答案：{q.get('correct_answer', '')}\n"
                    if q.get('explanation'):
                        txt += f"   解析：{q['explanation']}\n"

                txt += "\n"

        txt += f"\n{'-' * 50}\n"
        txt += f"生成時間：{timestamp}\n"

        return txt

    def export_to_json(
        self,
        article_text: str,
        questions: Optional[List[Dict]] = None,
        validation_result: Optional[Dict] = None,
        title: Optional[str] = None,
    ) -> str:
        """
        Export content to JSON format.

        Args:
            article_text: The article text
            questions: Optional list of questions
            validation_result: Optional validation result
            title: Document title

        Returns:
            JSON string
        """
        data = {
            "title": title or "華語閱讀理解練習",
            "timestamp": datetime.now().isoformat(),
            "article": {
                "text": article_text,
                "word_count": len(article_text),
            },
        }

        if questions:
            data["questions"] = questions

        if validation_result:
            data["validation_result"] = validation_result

        return json.dumps(data, ensure_ascii=False, indent=2)

    def export(
        self,
        article_text: str,
        format: ExportFormat,
        questions: Optional[List[Dict]] = None,
        validation_result: Optional[Dict] = None,
        include_answers: bool = True,
        include_validation: bool = False,
        title: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Export content to the specified format.

        Args:
            article_text: The article text
            format: Export format
            questions: Optional list of questions
            validation_result: Optional validation result
            include_answers: Whether to include answers
            include_validation: Whether to include validation report
            title: Document title

        Returns:
            Tuple of (content, filename)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"article_{timestamp}"

        if format == ExportFormat.HTML:
            content = self.export_to_html(
                article_text, questions, validation_result,
                include_answers, include_validation, title
            )
            filename = f"{base_filename}.html"

        elif format == ExportFormat.TXT:
            content = self.export_to_txt(
                article_text, questions, include_answers, title
            )
            filename = f"{base_filename}.txt"

        elif format == ExportFormat.JSON:
            content = self.export_to_json(
                article_text, questions, validation_result, title
            )
            filename = f"{base_filename}.json"

        else:
            raise ValueError(f"Unsupported export format: {format}")

        return content, filename

    @staticmethod
    def _format_text_to_html(text: str) -> str:
        """Format text with proper paragraphs for HTML."""
        paragraphs = text.split('\n')
        return ''.join([f"<p>{p.strip()}</p>\n" if p.strip() else "" for p in paragraphs])
