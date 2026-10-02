# 🛡️ Fake News & Text Engine

A **rule-based** news credibility checker and text analysis tool — built with Python, Streamlit, and Tkinter. No machine learning, no black box: every score is explainable.

---

## 📖 Overview

Fake News & Text Engine analyzes news headlines and articles for linguistic and structural patterns commonly associated with misleading content — sensational keywords, clickbait phrasing, excessive punctuation, ALL CAPS usage, thin content, and missing attribution.

For each piece of text, it generates:

- **Trust Score** (0–100)
- **Suspicion Level** — Low / Medium / High
- **Score Breakdown** — a transparent, rule-by-rule explanation of the result
- **Text Statistics** — word count, sentence count, paragraph count, average sentence length, reading level

Because the engine is keyword and rule-based rather than machine-learning-based, the same input always produces the same, explainable output.

---

## ✨ Features

- 🔍 **News Credibility Checker** — paste or upload text and get an instant Trust Score and Suspicion Level
- 📊 **Dashboard** — suspicion-level distribution and analysis activity, visualized with Plotly
- 📝 **Text Processing** — clean, transform, search, and replace text
- 📈 **Sentiment Analysis** — keyword-based positive/negative language detection
- 🔄 **Text Comparison** — compare two texts for similarity and shared patterns
- 📜 **History** — searchable, filterable analysis log with CSV export
- 📄 **Reports** — generate and export detailed per-analysis reports
- 🖥️ **Two interfaces** — a Streamlit web dashboard and a Tkinter desktop app, sharing one engine
- 🗄️ **SQLite storage** — analysis history, matched rules, and timestamps persisted locally

---

## 🧰 Tech Stack

| Purpose | Technology |
|---|---|
| Core engine & backend | Python |
| Web dashboard | Streamlit |
| Desktop app | Tkinter |
| Database | SQLite |
| Data handling | Pandas |
| Interactive charts | Plotly |
| Embedded charts (desktop) | Matplotlib |

---

## 📂 Project Structure

```
fake_news_text_engine/
├── streamlit_app.py        # Streamlit web dashboard
├── tkinter_app.py          # Tkinter desktop app
├── main.py                 # Entry point
├── database.py             # SQLite connection & queries
├── auth_db.py              # User authentication
├── engine/
│   ├── fake_news_detector.py
│   ├── sentiment.py
│   ├── sorting_utils.py
│   ├── text_processor.py
│   ├── comparison.py
│   ├── readability.py
│   ├── report_generator.py
│   └── search_replace.py
├── gui/                     # Tkinter UI components
├── utils/                   # Shared helper utilities
├── data/
│   ├── keywords.txt
│   ├── clickbait_words.txt
│   ├── suspicious_words.txt
│   ├── positive_words.txt
│   ├── negative_words.txt
│   ├── sample_news.txt
│   └── sample_suspicious_news.txt
├── reports/                 # Generated report exports
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/guldagadnikita/fake-news-text-engine.git
cd fake-news-text-engine

# Create a virtual environment
python -m venv venv
venv\Scripts\activate        # On Windows
source venv/bin/activate     # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Web App (Streamlit)

```bash
streamlit run streamlit_app.py
```

Then open `http://localhost:8501` in your browser.

### Running the Desktop App (Tkinter)

```bash
python tkinter_app.py
```

---

## 📊 How the Scoring Works

| Score Range | Suspicion Level |
|---|---|
| 66 – 100 | 🟢 Low Suspicion |
| 36 – 65 | 🟡 Medium Suspicion |
| 0 – 35 | 🔴 High Suspicion |

The score is calculated by checking the submitted text against a defined set of rules (sensational/conspiracy keywords, clickbait phrases, punctuation and capitalization patterns, content length, and presence of credible sourcing). Each rule that fires is shown in the **Score Breakdown**, so the result is never a mystery.

---

## ⚠️ Limitations

- This tool flags **language patterns**, it does **not** independently verify facts.
- A low-suspicion score does not guarantee a story is true, and a high-suspicion score does not guarantee it is false.
- Results should be treated as a **signal**, not a verdict.

---

## 🛣️ Future Enhancements

- Expand keyword and rule coverage
- Optional AI-assisted explanation mode
- Integration with external fact-checking APIs
- URL-based article analysis
- Cloud deployment

---

## 👤 Author

**Nikita Prashant Guldagad**
B.E. Computer Engineering, AISSMS IOIT
Developed as part of the AI Skill Training Program

---

## 📄 License

This project is available for educational purposes. Add a license of your choice (MIT, Apache 2.0, etc.) if you plan to share or distribute it publicly.
