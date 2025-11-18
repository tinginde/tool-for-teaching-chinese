# 華語教材智能生成器 - Claude Code 開發指引

> **專案目標**: 開發一個華語教材生成工具，參加「2025 華語文教學應用競賽：語料庫×能力基準×AI」數位工具組

---

## 📋 專案背景

### 競賽需求摘要
- **競賽組別**: 數位工具組
- **目標使用者**: 大學語言中心的華語教師
- **核心功能**: 教師輸入語法點和生詞 → 系統生成閱讀理解文章
- **關鍵要求**: 
  - 符合臺灣華語文能力基準 (TBCL)
  - 具教學或學習輔助功能
  - 可供評審測試和檢視
  - 遵守資料隱私和著作權規範

### 使用者需求分析
- **使用者**: 大學語言中心華語教師
- **痛點**: 
  - 備課時間長（每週 6-9 小時準備教材）
  - 找不到完全符合教學目標的現成教材
  - 希望教材有趣但又要涵蓋特定語法和詞彙
- **使用情境**:
  - 週末備課：為下週課程準備 2-3 篇閱讀文章
  - 考前準備：快速生成期中/期末測驗的閱讀理解題
  - 客製化教材：針對特定學生群體調整教材難度

---

## 🎯 核心功能定義

### MVP 必備功能（Phase 1 - 3 週）

#### F1: 語法點輸入模組 (P0)
- 支援自由文字輸入或從預設清單選擇
- 每次可輸入 1-5 個語法點
- 顯示語法點對應的 TBCL 等級
- 至少支援 30 個常見語法點

#### F2: 生詞輸入模組 (P0)
- 支援批量輸入（逐行輸入或貼上清單）
- 每次可輸入 5-20 個生詞
- 可標註詞性（名詞、動詞、形容詞等）
- 自動檢測生詞的 TBCL 等級

#### F3: 文章生成引擎 (P0)
- 根據輸入的語法點和生詞生成 300-600 字文章
- 文章類型：日常生活故事、台灣文化介紹、簡化新聞報導、人物訪談
- 難度等級：對應 TBCL A2-C1
- 生成時間：< 30 秒
- 文章要求：有趣、有意義、連貫、語法正確

#### F4: 輸出準確性驗證機制 (P0) ⭐ **核心特色**
這是本專案的差異化競爭優勢！

**功能需求**:
1. **語法點檢測**
   - 使用規則匹配 (正則表達式) + AI 語義分析雙重驗證
   - 標註語法點在文章中的位置
   - 顯示每個語法點的使用次數
   - 判斷使用是否正確（語法檢查）
   - 準確率目標：≥ 90%

2. **生詞檢測**
   - 精確字串匹配
   - 統計每個生詞出現次數
   - 標註生詞在文章中的位置
   - 檢測是否有未出現的生詞
   - 準確率目標：100%

3. **視覺化呈現**
   - 生成的文章中，語法點用顏色 A 標註（例如：藍色）
   - 生詞用顏色 B 標註（例如：黃色）
   - 側邊欄顯示檢查清單：
     ```
     ✅ 把字句：出現 2 次
     ✅ 生詞「環境」：出現 1 次
     ⚠️ 生詞「保護」：未出現
     ```

4. **重新生成機制**
   - 如果檢測不通過，可一鍵重新生成
   - 保留檢測歷史，避免重複錯誤

**技術實作方向**:
- 正則表達式匹配語法結構
- jieba 分詞 + 詞性標註
- Claude API 二次驗證語法使用正確性
- 前端高亮顯示（React + CSS highlighting）

#### F5: 閱讀理解題目生成 (P0)
- 根據生成的文章，自動產生 3-5 題閱讀理解問題
- 題型：細節理解（2 題）、推論題（1 題）、詞彙題（1-2 題）
- 選擇題格式（4 選 1）
- 附標準答案和解析

#### F6: 基本編輯功能 (P1)
- 線上文字編輯器
- 可修改文章內容
- 修改後保留原始版本（版本對比）
- 修改後重新執行準確性檢測

#### F7: 基本匯出功能 (P1)
- 匯出為 HTML（可直接複製到 Word）
- 匯出為純文字（.txt）
- 包含：文章、題目、答案

### 未來擴展功能（Phase 2+ - 視時間而定）

#### F8: 進階匯出功能 (P2)
- 匯出為 PDF（含格式）
- 匯出為 DOCX（可編輯）
- 匯出為學習單格式

#### F9: 使用者帳號系統 (P2)
- 教師註冊/登入
- 儲存個人教材庫
- 教材分類管理

#### F10: 新聞改寫功能 (P2)
- 輸入新聞 URL
- 自動簡化到目標等級
- 融入指定語法點和生詞

---

## 🏗️ 技術架構

### 技術棧選擇

#### 前端
- **框架**: React 18.3+ with TypeScript
- **建置工具**: Vite 5.0+
- **樣式**: TailwindCSS 3.4+
- **狀態管理**: Zustand 4.5+
- **API 管理**: React Query 5.0+
- **HTTP**: Axios 1.6+

**選擇理由**:
- React + TypeScript: 型別安全、元件化開發
- Vite: 快速開發體驗、HMR
- TailwindCSS: 快速原型開發
- Zustand: 輕量級、易於測試

#### 後端
- **框架**: FastAPI 0.110+ (Python 3.11+)
- **AI SDK**: Anthropic SDK 0.25+
- **NLP 工具**: 
  - jieba 0.42+ (中文分詞)
  - spaCy 3.7+ (備選，用於更複雜的 NLP 任務)
- **ORM**: SQLAlchemy 2.0+
- **驗證**: Pydantic 2.6+
- **快取**: Redis 7.2+

**選擇理由**:
- FastAPI: 高效能、自動 API 文檔、異步支援
- Python: AI/NLP 生態系豐富，適合 prompt engineering
- jieba: 最成熟的中文分詞工具
- Redis: 快取 API 回應、rate limiting

#### 資料庫
- **主資料庫**: SQLite (MVP 階段)
- **快取**: Redis

**選擇理由**:
- SQLite: 輕量、無需額外配置、適合 MVP
- 未來可輕鬆遷移到 PostgreSQL

#### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx (生產環境)

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                         前端層 (Frontend)                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  輸入介面    │  │  文章展示    │  │  驗證視覺化  │      │
│  │  - 語法點    │  │  - 渲染文章  │  │  - 高亮標註  │      │
│  │  - 生詞      │  │  - 編輯器    │  │  - 檢查清單  │      │
│  │  - 設定      │  │  - 題目顯示  │  │  - 重新生成  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│                      React + TypeScript                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ RESTful API (JSON)
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                        後端層 (Backend)                        │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API 路由層 (FastAPI)                      │   │
│  │  /api/generate | /api/validate | /api/export         │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                            │                                  │
│  ┌────────────────────────┴─────────────────────────────┐   │
│  │                   業務邏輯層                           │   │
│  │                                                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │
│  │  │ 文章生成器   │  │ 驗證引擎     │  │ 題目生成  │ │   │
│  │  │ - Prompt工程 │  │ - 語法檢測   │  │ - Claude  │ │   │
│  │  │ - Claude API │  │ - 生詞檢測   │  │   API     │ │   │
│  │  │ - 品質控制   │  │ - 位置標註   │  │           │ │   │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│                     FastAPI + Python                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Claude API │  │   SQLite     │  │   Redis      │
│              │  │   - Sessions │  │   - 快取     │
│   Anthropic  │  │   - Records  │  │   - Rate     │
│   SDK        │  │   - Grammar  │  │     Limit    │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 📊 資料模型設計

### 核心資料表

#### 1. generation_sessions
儲存使用者 session（無需登入，但追蹤使用）

```sql
CREATE TABLE generation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_token VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- 30天後過期
    last_access TIMESTAMP
);
```

#### 2. material_records
儲存生成的教材記錄

```sql
CREATE TABLE material_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    
    -- 輸入
    grammar_points JSON NOT NULL,  -- [{"name": "把字句", "tbcl": "A2"}]
    vocabulary JSON NOT NULL,      -- [{"word": "環境", "pos": "N"}]
    tbcl_level VARCHAR(10),
    article_type VARCHAR(50),
    
    -- 輸出
    article_text TEXT NOT NULL,
    article_metadata JSON,
    questions JSON,
    
    -- 驗證結果 ⭐
    validation_result JSON NOT NULL,
    -- {
    --   grammar_check: [
    --     {name: "把字句", found: true, count: 2, 
    --      positions: [[12,18], [45,52]], correct: true}
    --   ],
    --   vocab_check: [
    --     {word: "環境", found: true, count: 1, positions: [[23,25]]}
    --   ],
    --   overall_pass: true,
    --   warnings: []
    -- }
    
    -- 編輯
    is_edited BOOLEAN DEFAULT FALSE,
    edit_history JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES generation_sessions(id)
);
```

#### 3. grammar_point_library
預設語法點資料庫

```sql
CREATE TABLE grammar_point_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    name_en VARCHAR(200),
    tbcl_level VARCHAR(10),
    description TEXT,
    pattern TEXT,  -- 檢測用的正則表達式
    examples JSON,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);
```

### Redis 快取設計

```python
# 快取 Key 命名規範
CACHE_KEYS = {
    "generation": "gen:{session_id}:{input_hash}",  # TTL: 1小時
    "validation": "val:{material_id}",  # TTL: 30分鐘
    "grammar_lib": "grammar:all",  # TTL: 24小時
}

# Rate Limiting
RATE_LIMITS = {
    "/api/generate": (20, 3600),  # 每小時20次
    "/api/validate": (100, 3600),
}
```

---

## 🔌 API 設計

### Base URL
```
http://localhost:8000/api/v1
```

### 核心 API 端點

#### 1. 初始化 Session
```http
POST /api/session/init
```

Response:
```json
{
  "session_token": "uuid-string",
  "expires_at": "2025-12-19T00:00:00Z"
}
```

#### 2. 生成文章 ⭐ 核心 API
```http
POST /api/generate
Content-Type: application/json

{
  "grammar_points": [
    {"name": "把字句", "tbcl": "A2"},
    {"name": "比較句", "tbcl": "A2"}
  ],
  "vocabulary": [
    {"word": "環境", "pos": "N"},
    {"word": "保護", "pos": "V"},
    {"word": "重要", "pos": "Adj"}
  ],
  "settings": {
    "tbcl_level": "A2",
    "article_type": "daily_life",
    "word_count": 500
  }
}
```

Response:
```json
{
  "material_id": 123,
  "article": {
    "title": "保護環境，從我做起",
    "text": "...",
    "metadata": {
      "word_count": 487,
      "difficulty_score": 0.65
    }
  },
  "validation": {
    "grammar_check": [
      {
        "name": "把字句",
        "found": true,
        "count": 2,
        "positions": [[12, 18], [45, 52]],
        "correct": true,
        "examples": ["我把垃圾放進垃圾桶", "他把環境保護得很好"]
      }
    ],
    "vocab_check": [
      {
        "word": "環境",
        "found": true,
        "count": 3,
        "positions": [[23, 25], [67, 69], [102, 104]]
      },
      {
        "word": "保護",
        "found": true,
        "count": 2,
        "positions": [[30, 32], [89, 91]]
      }
    ],
    "overall_pass": true,
    "warnings": []
  },
  "questions": [
    {
      "id": 1,
      "type": "detail",
      "question": "文章中提到保護環境的第一步是什麼？",
      "options": ["A. 減少用水", "B. 垃圾分類", "C. 節省電力", "D. 多種樹"],
      "answer": "B",
      "explanation": "根據文章第二段..."
    }
  ]
}
```

#### 3. 驗證文章 ⭐ 核心 API
```http
POST /api/validate
Content-Type: application/json

{
  "material_id": 123,
  "article_text": "edited text...",
  "grammar_points": [...],
  "vocabulary": [...]
}
```

Response: (同上 validation 格式)

#### 4. 重新生成
```http
POST /api/regenerate
Content-Type: application/json

{
  "material_id": 123,
  "reason": "missing_vocab",  // 或 "grammar_incorrect"
  "keep_settings": true
}
```

#### 5. 匯出
```http
GET /api/export/{material_id}?format=html
```

Formats: `html`, `txt`, `pdf` (Phase 2), `docx` (Phase 2)

---

## 🤖 AI Prompt 工程規格

### 文章生成 Prompt 模板

```python
ARTICLE_GENERATION_PROMPT = """
你是一位經驗豐富的華語教師和教材編寫專家。請根據以下要求生成一篇閱讀理解文章。

## 教學目標
**目標語法點**：
{grammar_points_formatted}

**目標生詞**：
{vocabulary_formatted}

## 文章要求
- **TBCL 等級**：{tbcl_level}
- **文章類型**：{article_type}
- **目標字數**：{word_count} 字（±50字）
- **難度**：適合 {tbcl_level} 學習者閱讀

## 內容要求
1. 文章必須自然流暢，有清晰的起承轉合
2. 每個語法點至少使用 1-2 次，且用法必須正確
3. 每個生詞至少出現 1 次，且用法自然
4. 內容要有趣或有教育意義，避免生硬的教學範例
5. 符合台灣的語言習慣和文化背景
6. 適合作為課堂閱讀教材

## 輸出格式
請以 JSON 格式輸出：
{{
  "title": "文章標題",
  "text": "文章正文",
  "summary": "文章摘要（1-2句）",
  "difficulty_notes": "難度說明或教學建議"
}}

## 範例參考
[根據文章類型提供 few-shot examples]

請開始生成文章。
"""
```

### 語法驗證 Prompt 模板

```python
GRAMMAR_VALIDATION_PROMPT = """
請分析以下文章中指定語法點的使用是否正確。

## 文章內容
{article_text}

## 需要檢查的語法點
{grammar_point_name}：{grammar_point_description}

## 檢測到的使用位置
{detected_usage}

## 請評估
1. 這些使用是否符合該語法點的定義？
2. 語法使用是否正確、自然？
3. 是否有其他位置也使用了此語法點但未被檢測到？

請以 JSON 格式回覆：
{{
  "is_correct": true/false,
  "confidence": 0.0-1.0,
  "issues": ["問題描述..."],
  "missed_instances": ["未檢測到的使用..."],
  "suggestions": ["改進建議..."]
}}
"""
```

### 題目生成 Prompt 模板

```python
QUESTION_GENERATION_PROMPT = """
請根據以下文章生成 {num_questions} 道閱讀理解題目。

## 文章
{article_text}

## 題目要求
- 包含不同類型：細節理解（60%）、推論（30%）、詞彙（10%）
- 選擇題格式，4 個選項
- 難度符合 {tbcl_level}
- 每題附標準答案和詳細解析

## 輸出格式
[{{
  "type": "detail/inference/vocabulary",
  "question": "問題內容",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "B",
  "explanation": "詳細解析",
  "target_skill": "測試的能力"
}}]
"""
```

---

## 🧪 準確性驗證引擎實作細節

這是本專案的**核心競爭優勢**，需要特別投入開發資源。

### 實作策略：混合式驗證

#### 階段 1: 規則匹配（快速、準確）

**生詞檢測** (目標準確率: 100%)
```python
def detect_vocabulary(article_text: str, vocab_list: List[str]) -> Dict:
    """
    使用精確字串匹配檢測生詞
    """
    results = []
    for word in vocab_list:
        positions = []
        start = 0
        while True:
            pos = article_text.find(word, start)
            if pos == -1:
                break
            positions.append([pos, pos + len(word)])
            start = pos + 1
        
        results.append({
            "word": word,
            "found": len(positions) > 0,
            "count": len(positions),
            "positions": positions
        })
    
    return {"vocab_check": results}
```

**語法點檢測** (目標準確率: 90%)
```python
import re
import jieba.posseg as pseg

# 語法點的正則模式庫
GRAMMAR_PATTERNS = {
    "把字句": r"把[\u4e00-\u9fa5]{1,10}[給]?[\u4e00-\u9fa5]{1,10}",
    "被動句": r"被[\u4e00-\u9fa5]{1,10}[了]?",
    "比較句": r"比[\u4e00-\u9fa5]{1,10}[更還]?[\u4e00-\u9fa5]{1,5}",
    # ... 更多語法點模式
}

def detect_grammar_pattern(article_text: str, grammar_name: str) -> List:
    """
    使用正則表達式檢測語法點
    """
    pattern = GRAMMAR_PATTERNS.get(grammar_name)
    if not pattern:
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

def detect_grammar_by_segmentation(article_text: str, grammar_name: str) -> List:
    """
    使用 jieba 分詞和詞性標註輔助檢測
    例如：檢測「把」字句時，找「把」+ 動詞 的結構
    """
    words = pseg.cut(article_text)
    # 根據不同語法點實作不同的檢測邏輯
    # ...
    pass
```

#### 階段 2: AI 語義驗證（確保正確性）

```python
async def validate_grammar_with_claude(
    article_text: str,
    grammar_name: str,
    detected_instances: List[Dict]
) -> Dict:
    """
    使用 Claude API 驗證語法使用是否正確
    """
    prompt = GRAMMAR_VALIDATION_PROMPT.format(
        article_text=article_text,
        grammar_point_name=grammar_name,
        grammar_point_description=get_grammar_description(grammar_name),
        detected_usage=format_detected_instances(detected_instances)
    )
    
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 解析 Claude 的回應
    validation_result = parse_validation_response(response.content[0].text)
    
    return validation_result
```

#### 階段 3: 整合與視覺化

```python
async def comprehensive_validation(
    article_text: str,
    grammar_points: List[Dict],
    vocabulary: List[Dict]
) -> Dict:
    """
    完整的驗證流程
    """
    # 1. 生詞檢測（規則匹配）
    vocab_results = detect_vocabulary(
        article_text,
        [v["word"] for v in vocabulary]
    )
    
    # 2. 語法點檢測（規則匹配 + 分詞）
    grammar_results = []
    for grammar in grammar_points:
        pattern_matches = detect_grammar_pattern(
            article_text,
            grammar["name"]
        )
        
        # 3. AI 驗證（僅當有檢測結果時）
        if pattern_matches:
            ai_validation = await validate_grammar_with_claude(
                article_text,
                grammar["name"],
                pattern_matches
            )
            
            grammar_results.append({
                "name": grammar["name"],
                "found": True,
                "count": len(pattern_matches),
                "positions": [m["position"] for m in pattern_matches],
                "correct": ai_validation["is_correct"],
                "confidence": ai_validation["confidence"],
                "issues": ai_validation["issues"],
                "examples": [m["text"] for m in pattern_matches]
            })
        else:
            grammar_results.append({
                "name": grammar["name"],
                "found": False,
                "count": 0,
                "positions": [],
                "correct": False
            })
    
    # 4. 整體評估
    overall_pass = (
        all(v["found"] for v in vocab_results["vocab_check"]) and
        all(g["found"] and g["correct"] for g in grammar_results)
    )
    
    return {
        "grammar_check": grammar_results,
        "vocab_check": vocab_results["vocab_check"],
        "overall_pass": overall_pass,
        "warnings": generate_warnings(grammar_results, vocab_results)
    }
```

### 前端視覺化實作

```typescript
// React 元件：高亮顯示語法點和生詞
interface HighlightedTextProps {
  text: string;
  grammarPositions: Array<{name: string, positions: number[][]}>;
  vocabPositions: Array<{word: string, positions: number[][]}>;
}

const HighlightedText: React.FC<HighlightedTextProps> = ({
  text,
  grammarPositions,
  vocabPositions
}) => {
  // 建立標註區間陣列
  const annotations = [];
  
  grammarPositions.forEach(g => {
    g.positions.forEach(pos => {
      annotations.push({
        start: pos[0],
        end: pos[1],
        type: 'grammar',
        label: g.name,
        color: 'blue'
      });
    });
  });
  
  vocabPositions.forEach(v => {
    v.positions.forEach(pos => {
      annotations.push({
        start: pos[0],
        end: pos[1],
        type: 'vocab',
        label: v.word,
        color: 'yellow'
      });
    });
  });
  
  // 排序並渲染
  annotations.sort((a, b) => a.start - b.start);
  
  // 渲染邏輯（避免重疊標註）
  return <div className="highlighted-text">{renderWithHighlights(text, annotations)}</div>;
};
```

---

## 📅 開發時程規劃（5 週）

### Week 1-2: 核心功能開發
**後端優先**
- [x] Day 1-2: 專案結構建立、資料庫設計
- [ ] Day 3-5: Claude API 整合、文章生成引擎
- [ ] Day 6-8: **準確性驗證引擎**（核心！）
  - 生詞檢測
  - 語法點規則匹配
  - Claude API 語法驗證
  - 整合驗證流程
- [ ] Day 9-10: 題目生成 API
- [ ] Day 11-12: 基本編輯和匯出 API

**前端同步**
- [ ] Day 1-3: React 專案建立、路由設計
- [ ] Day 4-6: 輸入表單元件（語法點、生詞）
- [ ] Day 7-10: 文章展示和編輯元件
- [ ] Day 11-12: **驗證視覺化元件**（核心！）

### Week 3: 整合與優化
- [ ] Day 1-2: 前後端整合
- [ ] Day 3-4: 端到端測試
- [ ] Day 5-6: 效能優化（快取、rate limiting）
- [ ] Day 7: Bug 修復

### Week 4: 使用者測試
- [ ] Day 1-2: 邀請 3-5 位教師進行測試
- [ ] Day 3-4: 收集回饋、調整功能
- [ ] Day 5-7: 根據回饋優化

### Week 5: 競賽準備
- [ ] Day 1-2: 撰寫使用說明書
- [ ] Day 3-4: 錄製操作示範影片（< 3 分鐘）
- [ ] Day 5-6: 技術文檔整理、TBCL 對應表
- [ ] Day 7: 最終檢查、提交準備

---

## 📝 競賽提交清單

### 必備文件

#### 1. 使用說明書
**必須包含**:
- ✅ 快速入門指南（操作示範影片優先）
- ✅ 技術說明（開發環境、技術棧、AI 模型）
- ✅ 應用情境與價值（解決的具體教學問題）

#### 2. 操作示範影片
- 長度：2-3 分鐘
- 內容：
  1. 輸入語法點和生詞（30秒）
  2. 生成文章並展示（30秒）
  3. **準確性驗證展示**（60秒）⭐ 重點
  4. 編輯和匯出（30秒）

#### 3. 技術文檔
- 系統架構圖
- 資料庫 Schema
- API 規格
- **準確性驗證機制詳細說明**
- 使用的 AI 模型和 prompt 設計

#### 4. TBCL 標準對應表
```
語法點 | TBCL 等級 | 說明
把字句 | A2 | 基本把字句結構
被動句 | B1 | 基本被動式
比較句 | A2 | 使用「比」的比較
...
```

---

## 🎯 成功指標

### 技術指標
- [ ] 語法點檢測準確率 ≥ 90%
- [ ] 生詞檢測準確率 = 100%
- [ ] 文章生成時間 < 30 秒
- [ ] 驗證時間 < 5 秒
- [ ] 系統穩定性 > 95%

### 使用者滿意度
- [ ] 教師測試滿意度 ≥ 4/5
- [ ] 生成文章品質 ≥ 4/5
- [ ] 減少備課時間 ≥ 60%
- [ ] 願意推薦比例 ≥ 80%

### 競賽評分重點
- [ ] **技術創新性**：混合式驗證機制（規則 + AI）
- [ ] **實用性**：真實解決教師痛點
- [ ] **完整性**：功能完整、可測試
- [ ] **文檔品質**：清楚易懂的使用說明

---

## 🚨 風險管理

| 風險 | 影響 | 緩解措施 | 負責人 |
|------|------|----------|--------|
| API 費用超支 | 高 | 設定每日上限、快取機制、監控儀表板 | 開發 |
| 語法檢測不準確 | 高 | 雙重驗證、增加測試案例、提供手動調整 | 開發 |
| 文章品質不穩定 | 中 | 優化 prompt、few-shot examples、人工審核建議 | 開發 |
| 開發時間不足 | 中 | 聚焦 MVP、Phase 2 功能延後 | PM |
| 評審無法測試 | 高 | Demo 環境、詳細影片、備用方案 | 全員 |

---

## 💡 開發提示

### 給 Claude Code 的指令範例

#### 開始開發時
```
請幫我建立華語教材生成器的專案結構，根據 claude.md 的規格。
請先建立後端 FastAPI 專案，包含：
1. 專案結構（app/ 目錄）
2. 資料庫模型（SQLAlchemy）
3. API 路由骨架
4. Claude API 整合模組
```

#### 實作核心功能時
```
請實作準確性驗證引擎，這是專案的核心功能。需要：
1. 生詞檢測函式（精確字串匹配）
2. 語法點檢測函式（正則表達式 + jieba 分詞）
3. Claude API 語法驗證函式
4. 整合驗證流程

請參考 claude.md 中「準確性驗證引擎實作細節」章節。
```

#### 前端開發時
```
請建立 React 前端專案，需要：
1. 輸入表單元件（語法點、生詞）
2. 文章展示元件
3. 驗證視覺化元件（高亮標註語法點和生詞）

請使用 TypeScript + TailwindCSS，參考 claude.md 的技術棧。
```

### 開發原則
1. **測試驅動**：核心功能（驗證引擎）先寫測試
2. **漸進式開發**：從簡單功能開始，逐步增加複雜度
3. **持續測試**：每個功能完成後立即測試
4. **文檔同步**：重要決策和變更更新到文檔

---

## 📚 參考資源

### TBCL 資源
- [臺灣華語文能力基準官網](https://coct.naer.edu.tw/TBCL/)
- [TBCL 語法點列表](https://coct.naer.edu.tw/TBCL/grammar)
- [TBCL 詞彙表](https://coct.naer.edu.tw/TBCL/vocabulary)

### 技術文檔
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [React 官方文檔](https://react.dev/)
- [jieba 中文分詞](https://github.com/fxsjy/jieba)

### 競賽資訊
- [競賽官網](https://www.naer.edu.tw/)
- [競賽規則 PDF](https://www.naer.edu.tw/upload/1/14/doc/5284/%E3%80%8C2025%E8%8F%AF%E8%AA%9E%E6%96%87%E6%95%99%E5%AD%B8%E6%87%89%E7%94%A8%E7%AB%B6%E8%B3%BD%EF%BC%9A%E8%AA%9E%E6%96%99%E5%BA%AB%C3%97%E8%83%BD%E5%8A%9B%E5%9F%BA%E6%BA%96%C3%97AI%E3%80%8D%E8%A8%88%E7%95%AB_%E5%85%AC%E5%91%8A%E7%89%88.pdf)

---

## 🎉 預期成果

### 產品成果
- 一個功能完整的華語教材生成工具
- 能在 30 秒內生成高品質閱讀文章
- **準確性驗證機制成為差異化優勢**
- 大幅減少教師備課時間（60%+）

### 技術成果
- 掌握 AI prompt 工程技巧
- 學習混合式驗證方法（規則 + AI）
- 全端開發經驗（React + FastAPI）
- NLP 實務應用（中文分詞、語法檢測）

### 競賽成果
- 完整的作品展示（程式碼 + 文檔 + 影片）
- 突出的技術創新點（驗證機制）
- 真實的使用者回饋和測試數據
- 符合 TBCL 標準的教學應用

---

## 📞 聯絡資訊

- **開發者**: Tina
- **專案目的**: 2025 華語文教學應用競賽
- **開發期間**: 2025年11月-12月（5週）
- **技術支援**: Claude Code + Claude API

---

**版本歷史**
- v1.0 (2025-11-19): 初始版本，完整專案規格
- v1.1 (TBD): 根據開發過程更新

---

**祝開發順利！🚀**