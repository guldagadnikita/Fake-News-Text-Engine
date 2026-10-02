# 🛡️ FAKE NEWS & TEXT PROCESSING ENGINE

**Detect • Analyze • Process • Understand**

> A professional rule-based text analysis platform for detecting suspicious news content, processing text, extracting patterns, and generating meaningful analysis insights.

---

## 🚀 Quick Start

### Run Web Application (Streamlit)
```bash
python -m streamlit run streamlit_app.py
```
Then open **http://localhost:8501** in your browser.

### Run Desktop Application (Tkinter)
```bash
python tkinter_app.py
```
or
```bash
python main.py
```

---

## 📋 Features

| Feature | Description |
|---|---|
| 🔐 User Authentication | Register, login, secure password hashing (SHA-256 + salt) |
| 📊 Dashboard | Per-user stats: analyses, suspicion counts, words analyzed |
| 🔍 Fake News Detection | Rule-based scoring with detailed score breakdown |
| 📝 Text Processing | Clean, transform, search, replace text |
| 📈 Text Analysis | Statistics, readability, sentiment, word frequency |
| 🔄 Text Comparison | Side-by-side comparison with similarity score |
| 📜 History | Full per-user analysis history with filters |
| 📄 Reports | Generate and download TXT analysis reports |
| ⚙️ Settings | Profile management, password change |

---

## 🏗️ Architecture

```
FAKE NEWS & TEXT PROCESSING ENGINE
│
├── engine/                    ← Core backend (pure Python)
│   ├── text_processor.py      ← Tokenize, stats, clean, transform
│   ├── fake_news_detector.py  ← Rule-based suspicion scoring
│   ├── sorting_utils.py       ← Bubble sort implementation
│   ├── search_replace.py      ← Search & replace functions
│   ├── readability.py         ← Flesch readability score
│   ├── sentiment.py           ← Keyword-based sentiment
│   ├── comparison.py          ← Text set comparison
│   ├── report_generator.py    ← Report string builder
│   └── file_handler.py        ← File I/O utilities
│
├── auth_db.py                 ← SQLite auth & history (shared by both UIs)
├── streamlit_app.py           ← Web UI (Streamlit)
├── tkinter_app.py             ← Desktop UI (Tkinter)
├── main.py                    ← Desktop app entry point
│
├── data/
│   ├── suspicious_words.txt
│   ├── clickbait_words.txt
│   ├── positive_words.txt
│   ├── negative_words.txt
│   ├── sample_news.txt
│   └── sample_suspicious_news.txt
│
└── reports/                   ← Generated reports saved here
```

Both UIs share the **same backend engine** and **same SQLite database**.

---

## 🔍 Detection Engine

The fake news detector is **fully rule-based** — no machine learning or external APIs.

### Scoring Signals:
| Signal | Points |
|---|---|
| Suspicious keywords | +5 per word (max 40) |
| Clickbait phrases | +8 per phrase (max 25) |
| Excessive punctuation (!!, ??) | +5 per cluster (max 20) |
| High ALL-CAPS ratio | +5 to +20 |
| Very short/brief text | +10 |
| Credible attribution found | −10 to −20 |

### Verdicts:
- **LOW SUSPICION** (0–35): Likely reliable
- **NEEDS VERIFICATION** (36–65): Check sources
- **HIGH SUSPICION** (66–100): Highly suspicious content

---

## 🔐 Authentication

- Passwords hashed with **SHA-256 + random salt** — never stored as plain text
- Uses **SQLite** (`app_data.db`) — no external database server needed
- All history and reports are **per-user** (isolated by user ID)

---

## 📦 Installation

### Requirements
```
Python 3.8+
Tkinter (included with Python on Windows)
streamlit>=1.20.0
plotly>=5.0.0
```

### Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🎓 Python Concepts Demonstrated

This project demonstrates all core Python concepts:

| Concept | Where Used |
|---|---|
| Variables & Data Types | All modules |
| Strings & String Methods | text_processor.py, fake_news_detector.py |
| Conditional Statements | Detection scoring, auth validation |
| Loops | Text tokenization, word frequency counting |
| Functions & Return Values | All engine modules |
| Lists, Tuples, Dicts, Sets | comparison.py, sorting_utils.py |
| File Handling | file_handler.py, report saving |
| Exception Handling | All modules with try/except |
| Modules & Packages | engine/ package, auth_db module |
| Searching | search_replace.py |
| Sorting (Bubble Sort) | sorting_utils.py |
| Classes (OOP) | FakeNewsApp class (Tkinter) |
| SQLite / Databases | auth_db.py |

---

## 📁 Project Info

**Organization:** Hope Foundation Python Training  
**Type:** College Mini Project — Rule-based NLP Text Analysis  
**Language:** Python (Tkinter + Streamlit)  
**Database:** SQLite (no external server required)  
**ML/AI:** None — fully rule-based and explainable
