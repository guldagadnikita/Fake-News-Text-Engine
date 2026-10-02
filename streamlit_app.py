import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import os
import sys
import io

# ── Project path ──────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Engine imports (unchanged) ────────────────────────────────────────────────
from engine.text_processor import (
    calculate_text_statistics, get_word_frequencies,
    tokenize_words, clean_extra_spaces, clean_line_breaks, format_sentence_case
)
from engine.fake_news_detector import calculate_fake_news_score
from engine.sorting_utils import bubble_sort_frequencies
from engine.search_replace import search_word_occurrences, replace_word_in_text
from engine.readability import calculate_readability_score, estimate_reading_time
from engine.sentiment import analyze_sentiment
from engine.comparison import compare_texts
from engine.report_generator import build_full_report
from engine.file_handler import read_text_file

from auth_db import (
    register_user, login_user, change_password, update_user_name,
    save_analysis, get_user_history, delete_analysis, clear_user_history,
    get_user_stats, save_report, get_user_reports, get_report_content,
)

# ── Midnight Blue + Cyan color palette ───────────────────────────────────────
COLOR_BG       = "#07111F"
COLOR_SIDEBAR  = "#0B1728"
COLOR_CARD     = "#102238"
COLOR_ELEVATED = "#162B44"
COLOR_ACCENT   = "#38BDF8"
COLOR_ACCENT2  = "#06B6D4"
COLOR_BORDER   = "#1E3A5F"
COLOR_TEXT     = "#F8FAFC"
COLOR_TEXT2    = "#94A3B8"
COLOR_LOW      = "#22C55E"
COLOR_MED      = "#F59E0B"
COLOR_HIGH     = "#EF4444"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fake News & Text Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS — Midnight Blue + Cyan ─────────────────────────────────────────
st.markdown(f"""
<style>
/* Base */
.stApp {{ background-color: {COLOR_BG}; color: {COLOR_TEXT}; }}
header {{visibility: hidden;}}
footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {COLOR_SIDEBAR} !important;
    border-right: 1px solid {COLOR_BORDER};
}}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {{
    background-color: {COLOR_ELEVATED} !important;
    border: 1px solid {COLOR_BORDER} !important;
    color: {COLOR_TEXT} !important;
    border-radius: 8px !important;
}}

/* Buttons */
.stButton > button {{
    background-color: {COLOR_ACCENT};
    color: #07111F;
    border-radius: 8px;
    font-weight: 700;
    border: none;
    transition: background 0.2s ease;
}}
.stButton > button:hover {{
    background-color: {COLOR_ACCENT2};
    color: #07111F;
}}
.stButton > button[kind="secondary"] {{
    background-color: transparent;
    color: {COLOR_TEXT2};
    border: 1px solid {COLOR_BORDER};
}}
.stButton > button[kind="secondary"]:hover {{
    background-color: {COLOR_ELEVATED};
    color: {COLOR_TEXT};
    border-color: {COLOR_ACCENT};
}}
.stButton > button[kind="primary"] {{
    background-color: {COLOR_ACCENT};
    color: #07111F;
    border: none;
}}

/* Metrics */
[data-testid="stMetricValue"] {{ color: {COLOR_ACCENT}; }}

/* Tabs */
.stTabs [data-baseweb="tab"] {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT2};
    border-bottom: 2px solid transparent;
}}
.stTabs [aria-selected="true"] {{
    color: {COLOR_ACCENT};
    border-bottom: 2px solid {COLOR_ACCENT};
}}

/* Container borders */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER} !important;
    border-radius: 12px !important;
}}

/* Chat */
[data-testid="stChatMessageContent"] {{
    background-color: {COLOR_ELEVATED} !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    color: {COLOR_TEXT} !important;
}}
[data-testid="stChatInput"] textarea {{
    background-color: {COLOR_ELEVATED} !important;
    border: 1px solid {COLOR_BORDER} !important;
    color: {COLOR_TEXT} !important;
    border-radius: 10px !important;
}}

/* Alerts */
.stAlert {{ border-radius: 8px !important; }}

/* Custom reusable classes */
.mc {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border-left: 3px solid {COLOR_ACCENT};
    margin-bottom: 0.5rem;
}}
.mc-label {{
    color: {COLOR_TEXT2};
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}}
.mc-value {{
    color: {COLOR_TEXT};
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1.1;
}}
.badge {{
    display: inline-block;
    border-radius: 999px;
    padding: 3px 12px;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
}}
.badge-low  {{ background: rgba(34,197,94,0.15);  color: {COLOR_LOW}; }}
.badge-med  {{ background: rgba(245,158,11,0.15); color: {COLOR_MED}; }}
.badge-high {{ background: rgba(239,68,68,0.15);  color: {COLOR_HIGH}; }}
.breakdown-row {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid {COLOR_BORDER};
}}
.check-pass {{ color: {COLOR_LOW}; font-weight: 700; font-size: 1rem; }}
.check-flag {{ color: {COLOR_HIGH}; font-weight: 700; font-size: 1rem; }}
.check-warn {{ color: {COLOR_MED}; font-weight: 700; font-size: 1rem; }}

/* Engine-rule cards on home */
.rule-card {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
}}
.rule-card-icon {{ font-size: 1.1rem; margin-bottom: 0.2rem; }}
.rule-card-title {{ color: {COLOR_TEXT}; font-weight: 600; font-size: 0.88rem; }}
.rule-card-desc  {{ color: {COLOR_TEXT2}; font-size: 0.78rem; margin-top: 0.15rem; }}

/* Score guide bar */
.score-guide {{
    display: flex;
    border-radius: 8px;
    overflow: hidden;
    height: 10px;
    margin: 0.5rem 0;
}}
.sg-low  {{ flex: 35; background: {COLOR_LOW}; }}
.sg-med  {{ flex: 30; background: {COLOR_MED}; }}
.sg-high {{ flex: 35; background: {COLOR_HIGH}; }}

/* Stat mini card */
.stat-mini {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    padding: 0.9rem;
    text-align: center;
}}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
_defaults = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_email": "",
    "current_page": "Home",
    "auth_mode": "Login",
    "detection_text": "",
    "last_analysis": None,
    "assistant_messages": [],
    "confirm_clear": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def navigate(page: str):
    st.session_state.current_page = page
    st.rerun()


def suspicion_badge(verdict: str) -> str:
    if verdict == "LOW SUSPICION":
        return "<span class='badge badge-low'>LOW SUSPICION</span>"
    elif verdict == "NEEDS VERIFICATION":
        return "<span class='badge badge-med'>MEDIUM SUSPICION</span>"
    elif verdict == "HIGH SUSPICION":
        return "<span class='badge badge-high'>HIGH SUSPICION</span>"
    return f"<span class='badge'>{verdict}</span>"


def verdict_color(verdict: str) -> str:
    if verdict == "LOW SUSPICION":      return COLOR_LOW
    if verdict == "NEEDS VERIFICATION": return COLOR_MED
    if verdict == "HIGH SUSPICION":     return COLOR_HIGH
    return COLOR_TEXT2


def make_plotly_config():
    return {"displayModeBar": False}


def plotly_dark_layout(title="", height=320):
    return {
        "paper_bgcolor": COLOR_CARD,
        "plot_bgcolor":  COLOR_CARD,
        "font":   {"color": COLOR_TEXT,  "family": "Inter, sans-serif"},
        "title":  {"text": title, "font": {"color": COLOR_TEXT, "size": 14}},
        "height": height,
        "margin": {"l": 20, "r": 20, "t": 40, "b": 20},
        "showlegend": True,
        "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": COLOR_TEXT2}},
        "xaxis": {"gridcolor": COLOR_BORDER, "linecolor": COLOR_BORDER,
                  "tickfont": {"color": COLOR_TEXT2}},
        "yaxis": {"gridcolor": COLOR_BORDER, "linecolor": COLOR_BORDER,
                  "tickfont": {"color": COLOR_TEXT2}},
    }


def metric_card_html(label, value, color=None, icon=""):
    c = color or COLOR_ACCENT
    return f"""
    <div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};border-radius:12px;
         padding:1.2rem 1.5rem;border-left:3px solid {c};margin-bottom:0.5rem;'>
      <div style='color:{COLOR_TEXT2};font-size:0.78rem;text-transform:uppercase;
           letter-spacing:0.06em;margin-bottom:0.4rem;'>{icon} {label}</div>
      <div style='color:{COLOR_TEXT};font-size:1.9rem;font-weight:700;'>{value}</div>
    </div>"""


def normalize_word_freq_pairs(items):
    normalized = []
    for item in items:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            normalized.append((item[0], item[1]))
        elif isinstance(item, dict):
            w = item.get("word", item.get("Word", "?"))
            c = item.get("count", item.get("Count", 0))
            normalized.append((w, c))
        elif isinstance(item, str):
            normalized.append((item, 1))
        elif isinstance(item, (int, float)):
            normalized.append(("?", item))
        else:
            normalized.append((str(item), 1))
    return normalized


# ── Rule-based Engine Assistant ───────────────────────────────────────────────
def _bot_reply(user_msg: str) -> str:
    """
    Pure rule-based keyword matching chatbot.
    No external API, no ML, no internet.
    """
    msg = user_msg.lower().strip()
    la  = st.session_state.last_analysis

    # ── Latest result / score explanation ─────────────────────────────────────
    result_triggers = [
        "latest result", "my result", "explain result", "my score",
        "why did i get", "why is my score", "what affected", "why was my text",
        "explain my", "score high", "score low", "flagged", "my analysis"
    ]
    if any(t in msg for t in result_triggers):
        if la is None:
            return (
                "I don't have a current analysis to explain yet.\n\n"
                "Please analyze some text in the **Credibility Checker** first, "
                "then come back here and ask me to explain your result."
            )
        d  = la["details"]
        sc = la["score"]
        v  = la["verdict"]
        ui_v = "LOW SUSPICION" if v == "LOW SUSPICION" else (
               "MEDIUM SUSPICION" if v == "NEEDS VERIFICATION" else "HIGH SUSPICION")

        parts = [
            f"**Your latest result:** Trust Score **{sc}/100** — {ui_v}",
            "",
            "**Score contributors:**"
        ]
        if d.get("suspicious_points", 0) > 0:
            words = ", ".join(d.get("suspicious_matches", [])[:5]) or "none"
            parts.append(f"• ⚠ Suspicious Keywords: **+{d['suspicious_points']} pts** "
                         f"({len(d.get('suspicious_matches', []))} match(es): {words})")
        if d.get("clickbait_points", 0) > 0:
            phrases = ", ".join(d.get("clickbait_matches", [])[:3]) or "none"
            parts.append(f"• ⚠ Clickbait Phrases: **+{d['clickbait_points']} pts** "
                         f"({len(d.get('clickbait_matches', []))} phrase(s): {phrases})")
        if d.get("punct_points", 0) > 0:
            parts.append(f"• ⚠ Excessive Punctuation: **+{d['punct_points']} pts** "
                         f"({d.get('punct_clusters', 0)} cluster(s) like !! or ??)")
        if d.get("caps_points", 0) > 0:
            parts.append(f"• ⚠ ALL-CAPS Ratio: **+{d['caps_points']} pts** "
                         f"({d.get('caps_ratio', 0)}% of words are ALL-CAPS)")
        if d.get("brevity_points", 0) > 0:
            parts.append(f"• ⚠ Brief Content: **+{d['brevity_points']} pts** "
                         f"(only {d.get('total_words', 0)} words — lacks context)")
        if d.get("credible_reduction", 0) > 0:
            cwords = ", ".join(d.get("credible_matches", [])[:4]) or "none"
            parts.append(f"• ✓ Credible Attribution: **-{d['credible_reduction']} pts** "
                         f"(found: {cwords})")
        else:
            parts.append("• ⚠ No credible attribution or sourcing indicators found.")

        if (d.get("suspicious_points", 0) == 0 and d.get("clickbait_points", 0) == 0
                and d.get("punct_points", 0) == 0 and d.get("caps_points", 0) == 0
                and d.get("brevity_points", 0) == 0):
            parts.append("\nNo major suspicion signals were detected.")

        parts += [
            "",
            f"**Final Score: {sc}/100**",
            "*The score reflects rule-based linguistic signals — it does not verify factual accuracy.*"
        ]
        return "\n".join(parts)

    # ── Score calculation ─────────────────────────────────────────────────────
    score_triggers = [
        "score calculated", "score calculation", "how is the score", "score work",
        "credibility score", "suspicion score", "how does the score", "what is the score",
        "score formula", "how score"
    ]
    if any(t in msg for t in score_triggers):
        return (
            "**How the Trust Score is calculated:**\n\n"
            "The engine starts with a **base score of 10** and adds or subtracts "
            "points based on six rule-based signals:\n\n"
            "| Signal | Points |\n"
            "|---|---|\n"
            "| Suspicious Keywords | +12 per match (max +40) |\n"
            "| Clickbait Phrases | +15 per phrase (max +30) |\n"
            "| Excessive Punctuation (!!, ??) | +10 to +15 |\n"
            "| ALL-CAPS Ratio (>15%) | +15 to +25 |\n"
            "| Brief / Thin Content (<20 words) | +10 |\n"
            "| Credible Attribution Found | -10 per match (max -30) |\n\n"
            "**Score ranges:**\n"
            "• 0–35 → LOW SUSPICION 🟢\n"
            "• 36–65 → MEDIUM SUSPICION 🟠\n"
            "• 66–100 → HIGH SUSPICION 🔴\n\n"
            "*Higher scores mean more suspicious linguistic or structural patterns detected. "
            "The score does not prove content is true or false.*"
        )

    # ── Detection rules ───────────────────────────────────────────────────────
    rules_triggers = [
        "what rules", "what does the engine check", "engine check", "rules does",
        "what signals", "detection rules", "what checks", "checks for", "how does it detect",
        "six rules", "what rule"
    ]
    if any(t in msg for t in rules_triggers):
        return (
            "**The engine evaluates these 6 rule-based signals:**\n\n"
            "1. **Suspicious Keywords** — Words like *shocking, exposed, conspiracy, miracle, "
            "secret, censored, bombshell, leaked* increase the score.\n\n"
            "2. **Clickbait Phrases** — Phrases like *you won't believe, doctors hate this, "
            "one weird trick, gone viral* raise the score significantly.\n\n"
            "3. **Excessive Punctuation** — Clusters like `!!`, `??`, `!?` are flagged "
            "(patterns common in sensational writing).\n\n"
            "4. **ALL-CAPS Ratio** — A high percentage of words in ALL-CAPS indicates "
            "shouting-style writing, a common pattern in misleading content.\n\n"
            "5. **Brief / Thin Content** — Very short text (under 20 words) lacks the "
            "context expected in credible reporting.\n\n"
            "6. **Credible Attribution** — Words like *according to, researchers, official, "
            "published, peer-reviewed* are credibility signals that reduce the score.\n\n"
            "*Only these 6 rules are used. No ML or external services are involved.*"
        )

    # ── Score guide ───────────────────────────────────────────────────────────
    if any(t in msg for t in ["score range", "score guide", "score mean", "what does score",
                               "0 to 100", "0–100", "green", "red", "amber", "verdict"]):
        return (
            "**Score Guide:**\n\n"
            "🟢 **0–35 — LOW SUSPICION**\n"
            "Few or no suspicious signals detected. The text may have credible attribution.\n\n"
            "🟠 **36–65 — MEDIUM SUSPICION (Needs Verification)**\n"
            "Some suspicious patterns present. Cross-reference with other sources.\n\n"
            "🔴 **66–100 — HIGH SUSPICION**\n"
            "Multiple strong suspicious signals detected in the text.\n\n"
            "*Higher scores = more suspicious patterns. The score is a linguistic signal — "
            "not a fact-check.*"
        )

    # ── Readability ───────────────────────────────────────────────────────────
    if any(t in msg for t in ["readability", "reading level", "grade level", "flesch",
                               "reading score", "reading ease"]):
        if la:
            r = la["readability"]
            rt = la["rt"]
            return (
                f"**Readability for your last analyzed text:**\n\n"
                f"• **Score:** {r.get('score', 'N/A'):.1f}\n"
                f"• **Reading Ease:** {r.get('reading_ease', 'N/A')}\n"
                f"• **Grade Level:** {r.get('grade_level', 'N/A')}\n"
                f"• **Interpretation:** {r.get('interpretation', 'N/A')}\n"
                f"• **Estimated Reading Time:** {rt.get('reading_time_str', 'N/A')}\n"
                f"• **Speaking Time:** {rt.get('speaking_time_str', 'N/A')}\n\n"
                "*Readability is calculated using the Flesch Reading Ease formula.*"
            )
        return (
            "Readability analysis uses the **Flesch Reading Ease** formula.\n\n"
            "It estimates how easy or difficult a text is to read based on "
            "sentence length and syllable count. The engine also estimates "
            "reading time and speaking time.\n\n"
            "Analyze some text in the **Credibility Checker** to see your readability scores."
        )

    # ── Sentiment ─────────────────────────────────────────────────────────────
    if any(t in msg for t in ["sentiment", "positive", "negative", "tone", "emotional",
                               "language tone"]):
        if la:
            s = la["sentiment"]
            return (
                f"**Sentiment for your last analyzed text:**\n\n"
                f"• **Overall Tone:** {s.get('predominant_tone', 'N/A')}\n"
                f"• **Positive:** {s.get('positive_pct', 0):.1f}% "
                f"({s.get('positive_count', 0)} words)\n"
                f"• **Negative:** {s.get('negative_pct', 0):.1f}% "
                f"({s.get('negative_count', 0)} words)\n"
                f"• **Neutral:** {s.get('neutral_pct', 0):.1f}%\n\n"
                "*Sentiment is keyword-based — it counts positive and negative words "
                "from predefined word lists.*"
            )
        return (
            "The **Sentiment Analysis** feature identifies positive and negative "
            "language in text using keyword matching.\n\n"
            "It counts words from predefined positive and negative word lists and "
            "reports the percentage of each tone.\n\n"
            "Analyze some text in the **Credibility Checker** to see sentiment results."
        )

    # ── Text stats ────────────────────────────────────────────────────────────
    if any(t in msg for t in ["text statistics", "word count", "sentence count",
                               "paragraph", "statistics", "stats", "text stats",
                               "average word", "unique words"]):
        if la:
            s = la["stats"]
            return (
                f"**Text Statistics for your last analyzed text:**\n\n"
                f"• **Words:** {s.get('total_words', 0)}\n"
                f"• **Unique Words:** {s.get('unique_words', 0)}\n"
                f"• **Characters (with spaces):** {s.get('characters_with_spaces', 0)}\n"
                f"• **Sentences:** {s.get('total_sentences', 0)}\n"
                f"• **Paragraphs:** {s.get('total_paragraphs', 0)}\n"
                f"• **Avg Word Length:** {s.get('average_word_length', 0):.1f} chars\n"
                f"• **ALL-CAPS Words:** {s.get('uppercase_words_count', 0)}\n"
            )
        return (
            "The engine computes these **text statistics**:\n\n"
            "Word count, unique words, character count, sentence count, "
            "paragraph count, average word length, uppercase word count, "
            "and punctuation count.\n\n"
            "Analyze some text in the **Credibility Checker** to see your stats."
        )

    # ── Word frequency / bubble sort ─────────────────────────────────────────
    if any(t in msg for t in ["word frequency", "frequent", "top words", "bubble sort",
                               "sorting", "most common"]):
        return (
            "**Word Frequency** counts how often each word appears in the text.\n\n"
            "The engine uses a manual **Bubble Sort** algorithm (taught in the course) "
            "to rank words by frequency. The top 15 most frequent words are displayed "
            "as a horizontal bar chart.\n\n"
            "This demonstrates: Lists, Tuples, Loops, and the Bubble Sort algorithm."
        )

    # ── Text processing ───────────────────────────────────────────────────────
    if any(t in msg for t in ["text processing", "clean", "uppercase", "lowercase",
                               "sentence case", "line break", "extra space", "transform"]):
        return (
            "The **Text Processing** page lets you:\n\n"
            "• **Clean Extra Spaces** — removes duplicate whitespace\n"
            "• **Remove Line Breaks** — joins broken lines into flowing text\n"
            "• **Sentence Case** — capitalizes the first letter of each sentence\n"
            "• **Search & Replace** — find a word and replace it throughout the text\n\n"
            "These use existing backend functions: `clean_extra_spaces()`, "
            "`clean_line_breaks()`, `format_sentence_case()`, and `replace_word_in_text()`."
        )

    # ── Search and replace ────────────────────────────────────────────────────
    if any(t in msg for t in ["search", "replace", "find and replace", "find word"]):
        return (
            "The **Search & Replace** tool is on the **Text Processing** page.\n\n"
            "Enter a word to find and a replacement word, then click Replace. "
            "It uses `replace_word_in_text()` from the backend and reports "
            "how many replacements were made."
        )

    # ── Comparison ────────────────────────────────────────────────────────────
    if any(t in msg for t in ["comparison", "compare", "similarity", "two texts",
                               "text a", "text b", "compare texts"]):
        return (
            "The **Text Comparison** page lets you paste two pieces of text side by side.\n\n"
            "It uses `compare_texts()` which applies **set operations** to find:\n"
            "• **Similarity %** — how similar the vocabularies are\n"
            "• **Common Words** — words that appear in both texts\n"
            "• **Unique to A / Unique to B** — words exclusive to each text\n\n"
            "This demonstrates: Sets, Set Intersection, and Set Difference."
        )

    # ── Reports ───────────────────────────────────────────────────────────────
    if any(t in msg for t in ["report", "generate report", "save report", "download"]):
        return (
            "After analyzing text in the **Credibility Checker**, go to the **Report** tab.\n\n"
            "You can:\n"
            "• **View** the full formatted report\n"
            "• **Save** it to the database (linked to your account)\n"
            "• **Download** it as a `.txt` file\n\n"
            "Reports include: Trust Score, Score Breakdown, Text Statistics, "
            "Readability, Sentiment, and Word Frequency."
        )

    # ── History ───────────────────────────────────────────────────────────────
    if any(t in msg for t in ["history", "past analysis", "previous analysis",
                               "my analyses", "past results"]):
        return (
            "The **History** page shows all your previous analyses.\n\n"
            "Features:\n"
            "• **Search** by text content\n"
            "• **Filter** by suspicion level (Low / Medium / High)\n"
            "• **Export** the full history as a CSV file\n"
            "• **Delete** individual records or clear all history\n\n"
            "All data is stored per-user in the SQLite database."
        )

    # ── Project overview ──────────────────────────────────────────────────────
    if any(t in msg for t in ["what is this", "what does this", "about this project",
                               "project", "features", "what can you do", "what can this",
                               "overview", "capabilities"]):
        return (
            "**Fake News & Text Processing Engine** is a rule-based text analysis platform.\n\n"
            "**Main features:**\n"
            "• 🔍 **News Credibility Checker** — Trust Score + Suspicion Level + Score Breakdown\n"
            "• 📝 **Text Processing** — Clean, transform, search & replace\n"
            "• 📈 **Text Statistics** — Word count, readability, sentiment\n"
            "• 🔄 **Text Comparison** — Compare two articles\n"
            "• 📊 **Analytics Dashboard** — Charts from your analysis history\n"
            "• 📄 **Reports** — Generate and download analysis reports\n"
            "• 📜 **History** — Browse, search, filter, and export past analyses\n\n"
            "*Everything is rule-based — no ML, no external APIs.*"
        )

    # ── Dashboard ─────────────────────────────────────────────────────────────
    if any(t in msg for t in ["dashboard", "overview", "charts", "donut", "analytics"]):
        return (
            "The **Dashboard** shows a live overview of all your analyses:\n\n"
            "• **4 metric cards** — Total analyzed, Low, Medium, High suspicion counts\n"
            "• **Donut chart** — Distribution of suspicion levels\n"
            "• **Line chart** — Analysis activity over time\n"
            "• **Recent analyses** — Your last 5 results\n"
            "• **Quick actions** — Navigate to Credibility Checker, Comparison, or History\n\n"
            "All numbers are real — taken directly from your history in the database."
        )

    # ── Authentication ────────────────────────────────────────────────────────
    if any(t in msg for t in ["login", "register", "account", "password", "sign in",
                               "sign out", "logout", "authentication"]):
        return (
            "The app uses **SQLite-based authentication**.\n\n"
            "• Passwords are hashed with **SHA-256 + random salt** — never stored as plain text.\n"
            "• Each user has their own private history, reports, and statistics.\n"
            "• You can update your name and change your password in **Settings**.\n"
            "• Use **Sign Out** in the sidebar to log out safely."
        )

    # ── Technology ────────────────────────────────────────────────────────────
    if any(t in msg for t in ["technology", "built with", "how is this built",
                               "what technology", "python", "streamlit", "sqlite",
                               "plotly", "pandas"]):
        return (
            "**Technology Stack:**\n\n"
            "• **Python** — core language\n"
            "• **Streamlit** — web UI framework\n"
            "• **SQLite** — local database (auth, history, reports)\n"
            "• **Plotly** — interactive charts\n"
            "• **Pandas** — data handling and CSV export\n\n"
            "**Python concepts demonstrated:**\n"
            "Variables, Data Types, Strings, Conditionals, Loops, Functions, "
            "Return Values, Lists, Tuples, Dicts, Sets, File Handling, "
            "Exception Handling, Modules, Packages, Searching, Bubble Sort."
        )

    # ── Greetings ─────────────────────────────────────────────────────────────
    if any(t in msg for t in ["hi", "hello", "hey", "good morning", "good afternoon",
                               "good evening", "how are you", "namaste"]):
        return (
            "Hello! 👋 I'm the **Engine Assistant**.\n\n"
            "I can help you understand:\n"
            "• How the Trust Score is calculated\n"
            "• What rules the engine checks\n"
            "• Your latest analysis result\n"
            "• Features like readability, sentiment, comparison, and reports\n\n"
            "What would you like to know?"
        )

    # ── Thanks ────────────────────────────────────────────────────────────────
    if any(t in msg for t in ["thank", "thanks", "ok", "okay", "got it", "understood",
                               "clear", "nice", "great"]):
        return "You're welcome! Feel free to ask anything else about the engine. 🛡️"

    # ── Unknown ───────────────────────────────────────────────────────────────
    return (
        "I can help with the **Fake News & Text Processing Engine**.\n\n"
        "Try asking about:\n"
        "• *How is the score calculated?*\n"
        "• *What rules does the engine check?*\n"
        "• *Explain my latest result*\n"
        "• *What is readability / sentiment / word frequency?*\n"
        "• *How does text comparison work?*\n"
        "• *How do reports work?*\n"
        "• *What technology is this built with?*"
    )


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_auth():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
          <div style="font-size:2.4rem; margin-bottom:0.4rem;">🛡️</div>
          <h1 style="color:{COLOR_ACCENT}; font-size:1.7rem; margin:0.2rem 0; font-weight:800;">
            FAKE NEWS &amp; TEXT ENGINE
          </h1>
          <p style="color:{COLOR_TEXT2}; font-size:0.88rem;">
            Detect &bull; Analyze &bull; Process &bull; Understand
          </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            if st.session_state.auth_mode == "Login":
                st.markdown(f"<h3 style='color:{COLOR_TEXT}; margin-top:0;'>Sign In</h3>",
                            unsafe_allow_html=True)
                email    = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_pw")
                if st.button("Sign In", use_container_width=True):
                    success, result = login_user(email, password)
                    if success:
                        st.session_state.logged_in    = True
                        st.session_state.user_id      = result["id"]
                        st.session_state.user_name    = result["name"]
                        st.session_state.user_email   = result["email"]
                        st.session_state.current_page = "Home"
                        st.rerun()
                    else:
                        st.error(result)
                if st.button("New here? Create an account", use_container_width=True):
                    st.session_state.auth_mode = "Register"
                    st.rerun()
            else:
                st.markdown(f"<h3 style='color:{COLOR_TEXT}; margin-top:0;'>Create Account</h3>",
                            unsafe_allow_html=True)
                name     = st.text_input("Full Name",         key="reg_name")
                email    = st.text_input("Email",             key="reg_email")
                password = st.text_input("Password",          type="password", key="reg_pw")
                confirm  = st.text_input("Confirm Password",  type="password", key="reg_conf")
                if st.button("Create Account", use_container_width=True):
                    if not name or not email or not password or not confirm:
                        st.error("All fields required.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif "@" not in email:
                        st.error("Invalid email address.")
                    else:
                        success, res = register_user(name, email, password)
                        if success:
                            st.success("Account created! Please sign in.")
                            st.session_state.auth_mode = "Login"
                            st.rerun()
                        else:
                            st.error(res)
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.auth_mode = "Login"
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:1.4rem 1rem 0.8rem;'>
          <div style='display:flex;align-items:center;gap:0.5rem;'>
            <span style='font-size:1.3rem;'>🛡️</span>
            <div>
              <div style='color:{COLOR_TEXT};font-weight:800;font-size:0.92rem;line-height:1.2;'>
                FAKE NEWS &amp; TEXT ENGINE
              </div>
              <div style='color:{COLOR_ACCENT};font-size:0.68rem;margin-top:1px;'>
                Detect &bull; Analyze &bull; Understand
              </div>
            </div>
          </div>
        </div>
        <hr style='border:none;border-top:1px solid {COLOR_BORDER};margin:0;'/>
        """, unsafe_allow_html=True)

        nav_items = [
            ("🏠",  "Home",                "Home"),
            ("📊",  "Dashboard",           "Dashboard"),
            ("🔍",  "Credibility Checker", "Credibility Checker"),
            ("📝",  "Text Processing",     "Text Processing"),
            ("📈",  "Analysis",            "Analysis"),
            ("🔄",  "Comparison",          "Comparison"),
            ("🤖",  "Engine Assistant",    "Engine Assistant"),
            ("📜",  "History",             "History"),
            ("📄",  "Reports",             "Reports"),
            ("⚙️", "Settings",            "Settings"),
        ]
        for icon, label, page_key in nav_items:
            is_active = st.session_state.current_page == page_key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                navigate(page_key)

        st.markdown(
            f"<hr style='border:none;border-top:1px solid {COLOR_BORDER};margin:1rem 0 0.5rem;'/>",
            unsafe_allow_html=True)
        st.markdown(f"""
        <div style='padding:0.4rem 1rem 0.2rem;'>
          <div style='color:{COLOR_TEXT2};font-size:0.72rem;'>Signed in as</div>
          <div style='color:{COLOR_TEXT};font-weight:700;font-size:0.88rem;'>
            {st.session_state.user_name}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="logout_btn"):
            for k in ["logged_in", "user_id", "user_name", "user_email"]:
                st.session_state[k] = False if k == "logged_in" else (
                    None if k == "user_id" else "")
            st.session_state.current_page = "Home"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_home():

    # ── 1. HERO ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:2.5rem 1rem 1.5rem;">
      <div style="display:inline-block; background:rgba(56,189,248,0.1);
           border:1px solid rgba(56,189,248,0.3); border-radius:999px;
           padding:0.25rem 1rem; margin-bottom:1rem;">
        <span style="color:{COLOR_ACCENT}; font-size:0.75rem; font-weight:700;
              letter-spacing:0.08em;">RULE-BASED TEXT ANALYSIS ENGINE</span>
      </div>
      <h1 style="font-size:2.6rem; font-weight:900; color:{COLOR_TEXT};
           margin:0.3rem 0; line-height:1.15;">
        FAKE NEWS &amp; TEXT<br>PROCESSING ENGINE
      </h1>
      <p style="color:{COLOR_ACCENT}; font-size:1.1rem; font-weight:500;
           margin:0.6rem 0 0.8rem;">
        Detect &bull; Analyze &bull; Process &bull; Understand
      </p>
      <p style="color:{COLOR_TEXT2}; font-size:0.93rem; max-width:560px;
           margin:0 auto; line-height:1.6;">
        Analyze textual content for suspicious linguistic and structural patterns,
        process text efficiently, and understand your results through clear scores
        and visual insights.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    # ── 2. TRY AN EXAMPLE ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:0.8rem;">
      <div style="color:{COLOR_TEXT}; font-size:1.05rem; font-weight:700;">Try an Example</div>
      <div style="color:{COLOR_TEXT2}; font-size:0.82rem; margin-top:0.2rem;">
        Explore the engine using sample content.
      </div>
    </div>
    """, unsafe_allow_html=True)

    ex1, ex2, ex3 = st.columns([1, 2, 1])
    with ex2:
        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown(f"""
            <div style="background:{COLOR_CARD}; border:1px solid {COLOR_BORDER};
                 border-top:3px solid {COLOR_HIGH}; border-radius:10px;
                 padding:1.1rem 1.1rem 0.7rem; margin-bottom:0.5rem; text-align:center;">
              <div style="font-size:1.2rem; margin-bottom:0.3rem;">⚠️</div>
              <div style="color:{COLOR_TEXT}; font-weight:700; font-size:0.9rem;
                   margin-bottom:0.3rem;">Suspicious Example</div>
              <div style="color:{COLOR_TEXT2}; font-size:0.78rem; line-height:1.5;
                   margin-bottom:0.6rem;">
                Test the engine with content containing patterns commonly
                associated with suspicious text.
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try Suspicious Example", use_container_width=True, key="try_susp"):
                try:
                    st.session_state.detection_text = read_text_file(
                        os.path.join(PROJECT_ROOT, "data", "sample_suspicious_news.txt"))
                    navigate("Credibility Checker")
                except Exception as e:
                    st.error(f"Could not load sample: {e}")

        with ec2:
            st.markdown(f"""
            <div style="background:{COLOR_CARD}; border:1px solid {COLOR_BORDER};
                 border-top:3px solid {COLOR_LOW}; border-radius:10px;
                 padding:1.1rem 1.1rem 0.7rem; margin-bottom:0.5rem; text-align:center;">
              <div style="font-size:1.2rem; margin-bottom:0.3rem;">✓</div>
              <div style="color:{COLOR_TEXT}; font-weight:700; font-size:0.9rem;
                   margin-bottom:0.3rem;">Reliable Example</div>
              <div style="color:{COLOR_TEXT2}; font-size:0.78rem; line-height:1.5;
                   margin-bottom:0.6rem;">
                Explore how the engine responds to content with credible
                attribution patterns.
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try Reliable Example", use_container_width=True, key="try_rel"):
                try:
                    st.session_state.detection_text = read_text_file(
                        os.path.join(PROJECT_ROOT, "data", "sample_news.txt"))
                    navigate("Credibility Checker")
                except Exception as e:
                    st.error(f"Could not load sample: {e}")

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    # ── 4. SCORE GUIDE ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:0.5rem;">
      <div style="color:{COLOR_TEXT}; font-size:1.0rem; font-weight:700;
           margin-bottom:0.4rem;">Score Guide</div>
      <div class="score-guide"><div class="sg-low"></div><div class="sg-med"></div><div class="sg-high"></div></div>
      <div style="display:flex; justify-content:space-between; margin-top:0.5rem;">
        <div style="text-align:left;">
          <div style="color:{COLOR_LOW}; font-weight:700; font-size:0.88rem;">0 – 35</div>
          <div style="color:{COLOR_TEXT2}; font-size:0.76rem;">LOW SUSPICION</div>
        </div>
        <div style="text-align:center;">
          <div style="color:{COLOR_MED}; font-weight:700; font-size:0.88rem;">36 – 65</div>
          <div style="color:{COLOR_TEXT2}; font-size:0.76rem;">NEEDS VERIFICATION</div>
        </div>
        <div style="text-align:right;">
          <div style="color:{COLOR_HIGH}; font-weight:700; font-size:0.88rem;">66 – 100</div>
          <div style="color:{COLOR_TEXT2}; font-size:0.76rem;">HIGH SUSPICION</div>
        </div>
      </div>
      <div style="color:{COLOR_TEXT2}; font-size:0.78rem; margin-top:0.5rem;">
        Higher scores indicate more suspicious linguistic or structural patterns.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    # ── 5. WHAT THE ENGINE CHECKS ─────────────────────────────────────────────
    st.markdown(f"""
    <div style="color:{COLOR_TEXT}; font-size:1.0rem; font-weight:700; margin-bottom:0.6rem;">
      What the Engine Checks
    </div>
    """, unsafe_allow_html=True)

    rules = [
        ("🔑", "Suspicious Keywords",    "Words like 'shocking', 'exposed', 'conspiracy', 'miracle'."),
        ("🎣", "Clickbait Phrases",      "Phrases like 'you won't believe', 'doctors hate this'."),
        ("❗", "Excessive Punctuation",  "Patterns like !!, ??, !? indicate sensational style."),
        ("🔠", "ALL-CAPS Ratio",         "High percentage of ALL-CAPS words — shouting style."),
        ("📏", "Brief / Thin Content",   "Very short text (under 20 words) lacks context."),
        ("📰", "Credible Attribution",   "Words like 'according to', 'researchers' reduce the score."),
    ]
    rc1, rc2, rc3 = st.columns(3)
    rule_cols = [rc1, rc2, rc3, rc1, rc2, rc3]
    for i, (icon, title, desc) in enumerate(rules):
        with rule_cols[i]:
            st.markdown(f"""
            <div class="rule-card">
              <div class="rule-card-icon">{icon}</div>
              <div class="rule-card-title">{title}</div>
              <div class="rule-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    # ── 6. DISCLAIMER ─────────────────────────────────────────────────────────
    st.info(
        "**Important** — This application uses keyword and rule-based analysis to identify "
        "linguistic and structural credibility signals. "
        "It does not independently verify facts or guarantee that content is true or false."
    )


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    hour     = datetime.datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
    date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
    st.markdown(f"""
    <div style='margin-bottom:1.5rem;'>
      <h2 style='color:{COLOR_TEXT};margin:0;'>{greeting}, {st.session_state.user_name}</h2>
      <p style='color:{COLOR_TEXT2};margin:0.2rem 0 0;font-size:0.88rem;'>
        {date_str} &nbsp;·&nbsp; Analyze text for suspicious linguistic and structural patterns
      </p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_user_stats(st.session_state.user_id)
    total = stats.get("total_analyses", 0)
    low   = stats.get("reliable",            0)
    med   = stats.get("needs_verification",  0)
    high  = stats.get("suspicious",          0)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(metric_card_html("Total Analyzed",   total, COLOR_ACCENT, "📊"), unsafe_allow_html=True)
    with m2: st.markdown(metric_card_html("Low Suspicion",    low,   COLOR_LOW,    "✅"), unsafe_allow_html=True)
    with m3: st.markdown(metric_card_html("Medium Suspicion", med,   COLOR_MED,    "⚠️"), unsafe_allow_html=True)
    with m4: st.markdown(metric_card_html("High Suspicion",   high,  COLOR_HIGH,   "🚨"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        if total > 0:
            fig = go.Figure(go.Pie(
                labels=["Low Suspicion", "Medium Suspicion", "High Suspicion"],
                values=[low, med, high],
                hole=0.6,
                marker_colors=[COLOR_LOW, COLOR_MED, COLOR_HIGH],
                textinfo="label+percent",
                hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"
            ))
            fig.update_layout(**plotly_dark_layout("Suspicion Distribution", 300))
            st.plotly_chart(fig, use_container_width=True, config=make_plotly_config())
        else:
            st.markdown(
                f"<div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};"
                f"border-radius:12px;padding:3rem;text-align:center;color:{COLOR_TEXT2};'>"
                "No data yet. Start analyzing!</div>", unsafe_allow_html=True)

    with c2:
        history = get_user_history(st.session_state.user_id, limit=50)
        if history:
            df_h  = pd.DataFrame(history)
            df_h["date"] = pd.to_datetime(df_h["created_at"]).dt.date
            daily = df_h.groupby("date").size().reset_index(name="count")
            fig2  = go.Figure(go.Scatter(
                x=daily["date"], y=daily["count"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color=COLOR_ACCENT, width=2),
                fillcolor=f"rgba(56,189,248,0.08)",
                marker=dict(color=COLOR_ACCENT, size=5),
                hovertemplate="%{x}: %{y} analyses<extra></extra>"
            ))
            fig2.update_layout(**plotly_dark_layout("Analysis Activity", 300))
            st.plotly_chart(fig2, use_container_width=True, config=make_plotly_config())
        else:
            st.markdown(
                f"<div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};"
                f"border-radius:12px;padding:3rem;text-align:center;color:{COLOR_TEXT2};'>"
                "No activity data yet.</div>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='color:{COLOR_TEXT};margin:1.5rem 0 0.8rem;'>Recent Analyses</h3>",
                unsafe_allow_html=True)
    if history:
        for rec in history[:5]:
            vc   = verdict_color(rec["verdict"])
            bh   = suspicion_badge(rec["verdict"])
            st.markdown(f"""
            <div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};border-radius:10px;
                 padding:0.8rem 1.1rem;margin-bottom:0.4rem;
                 display:flex;justify-content:space-between;align-items:center;'>
              <div style='flex:1;'>
                <div style='color:{COLOR_TEXT};font-size:0.88rem;'>
                  {rec["text_preview"][:80]}...
                </div>
                <div style='color:{COLOR_TEXT2};font-size:0.73rem;margin-top:0.15rem;'>
                  {rec["created_at"]}
                </div>
              </div>
              <div style='display:flex;align-items:center;gap:0.8rem;margin-left:1rem;'>
                <div style='color:{vc};font-weight:700;font-size:1.05rem;'>{rec["score"]}/100</div>
                {bh}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};"
            f"border-radius:12px;padding:2rem;text-align:center;color:{COLOR_TEXT2};'>"
            "No analyses yet. Try the Credibility Checker!</div>", unsafe_allow_html=True)

    st.markdown(f"<h3 style='color:{COLOR_TEXT};margin:1.5rem 0 0.8rem;'>Quick Actions</h3>",
                unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("🔍 Analyze News",  use_container_width=True): navigate("Credibility Checker")
    with q2:
        if st.button("🔄 Compare Texts", use_container_width=True): navigate("Comparison")
    with q3:
        if st.button("📜 View History",  use_container_width=True): navigate("History")


# ══════════════════════════════════════════════════════════════════════════════
# CREDIBILITY CHECKER
# ══════════════════════════════════════════════════════════════════════════════
def page_credibility_checker():
    st.markdown(f"""
    <div style='margin-bottom:1.4rem;'>
      <h1 style='color:{COLOR_TEXT};margin:0;font-size:1.75rem;font-weight:800;'>
        🔍 News Credibility Checker
      </h1>
      <p style='color:{COLOR_TEXT2};margin:0.3rem 0 0;font-size:0.88rem;'>
        Check the credibility of news articles using our keyword and rule-based detection engine.
      </p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3, _ = st.columns([1, 1, 1, 3])
    with b1:
        if st.button("📄 Load Suspicious Sample"):
            try:
                st.session_state.detection_text = read_text_file(
                    os.path.join(PROJECT_ROOT, "data", "sample_suspicious_news.txt"))
                st.rerun()
            except:
                st.error("Could not load sample.")
    with b2:
        if st.button("✅ Load Reliable Sample"):
            try:
                st.session_state.detection_text = read_text_file(
                    os.path.join(PROJECT_ROOT, "data", "sample_news.txt"))
                st.rerun()
            except:
                st.error("Could not load sample.")
    with b3:
        uploaded = st.file_uploader("", type=["txt"], label_visibility="collapsed")
        if uploaded:
            st.session_state.detection_text = uploaded.getvalue().decode("utf-8")

    text_input = st.text_area(
        "News Text",
        value=st.session_state.get("detection_text", ""),
        height=220,
        placeholder="Paste a news headline or article here to check its credibility..."
    )

    ac1, ac2, _ = st.columns([2, 1, 5])
    with ac1:
        analyze = st.button("🔍 Analyze Text", use_container_width=True)
    with ac2:
        if st.button("✕ Clear", use_container_width=True):
            st.session_state.detection_text = ""
            st.session_state.last_analysis  = None
            st.rerun()

    if analyze:
        if not text_input or not text_input.strip():
            st.warning("⚠ Please enter some text before analyzing.")
        elif len(text_input.strip()) < 10:
            st.warning("⚠ Text is too short. Please provide more content.")
        else:
            with st.spinner("Analyzing text patterns..."):
                score, verdict, color_hex, reasons, details = calculate_fake_news_score(text_input)
                stats       = calculate_text_statistics(text_input)
                readability = calculate_readability_score(text_input)
                rt          = estimate_reading_time(stats["total_words"])
                sentiment   = analyze_sentiment(text_input)
                freq        = get_word_frequencies(tokenize_words(text_input))
                sorted_freq, _, _, _ = bubble_sort_frequencies(list(freq.items()))
                save_analysis(st.session_state.user_id, text_input, score, verdict, stats["total_words"])
                st.session_state.last_analysis = {
                    "score": score, "verdict": verdict, "color": color_hex,
                    "reasons": reasons, "details": details, "stats": stats,
                    "readability": readability, "rt": rt, "sentiment": sentiment,
                    "sorted_freq": sorted_freq, "text": text_input,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

    if st.session_state.last_analysis:
        la      = st.session_state.last_analysis
        score   = la["score"];   verdict = la["verdict"]; color  = la["color"]
        details = la["details"]; stats   = la["stats"];   reasons = la["reasons"]
        readability = la["readability"]; rt = la["rt"]; sentiment = la["sentiment"]

        st.markdown(
            f"<hr style='border:none;border-top:1px solid {COLOR_BORDER};margin:1.5rem 0;'/>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='color:{COLOR_TEXT2};font-size:0.78rem;margin-bottom:1rem;'>"
            f"Analyzed at {la['timestamp']}</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style='background:{COLOR_CARD};border:1px solid {color};border-radius:12px;
                 padding:2rem;text-align:center;'>
              <div style='color:{COLOR_TEXT2};font-size:0.8rem;text-transform:uppercase;
                   letter-spacing:0.1em;margin-bottom:0.4rem;'>Trust Score</div>
              <div style='color:{color};font-size:4rem;font-weight:900;line-height:1;'>{score}</div>
              <div style='color:{COLOR_TEXT2};font-size:0.9rem;margin-bottom:0.8rem;'>out of 100</div>
              {suspicion_badge(verdict)}
              <div style='margin-top:1rem;background:{COLOR_ELEVATED};border-radius:8px;
                   height:7px;overflow:hidden;'>
                <div style='height:100%;width:{score}%;background:{color};border-radius:8px;'></div>
              </div>
              <div style='color:{COLOR_TEXT2};font-size:0.73rem;margin-top:0.4rem;'>
                {"Low" if score<=35 else "Medium" if score<=65 else "High"} Suspicion Level
              </div>
            </div>
            <div style='color:{COLOR_TEXT2};font-size:0.76rem;text-align:center;margin-top:0.4rem;'>
              *Higher score = more suspicious patterns
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"<h3 style='color:{COLOR_TEXT};margin-top:0;'>Score Breakdown</h3>",
                        unsafe_allow_html=True)
            rule_rows = [
                (details.get("suspicious_points", 0) > 0, "Suspicious Keywords",
                 f"+{details.get('suspicious_points', 0)} pts — "
                 f"{len(details.get('suspicious_matches', []))} match(es): "
                 f"{', '.join(details.get('suspicious_matches', [])[:4]) or 'none'}"),
                (details.get("clickbait_points", 0) > 0, "Clickbait Phrases",
                 f"+{details.get('clickbait_points', 0)} pts — "
                 f"{len(details.get('clickbait_matches', []))} phrase(s): "
                 f"{', '.join(details.get('clickbait_matches', [])[:3]) or 'none'}"),
                (details.get("punct_points", 0) > 0, "Excessive Punctuation (!!, ??)",
                 f"+{details.get('punct_points', 0)} pts — "
                 f"{details.get('punct_clusters', 0)} cluster(s)"),
                (details.get("caps_points", 0) > 0, "ALL-CAPS Ratio",
                 f"+{details.get('caps_points', 0)} pts — "
                 f"{details.get('caps_ratio', 0)}% of words in ALL-CAPS"),
                (details.get("brevity_points", 0) > 0, "Brief / Thin Content",
                 f"+{details.get('brevity_points', 0)} pts — "
                 f"{details.get('total_words', 0)} words"),
                (details.get("credible_reduction", 0) > 0, "Credible Attribution Found",
                 f"-{details.get('credible_reduction', 0)} pts — "
                 f"{', '.join(details.get('credible_matches', [])[:4]) or 'none'}"),
            ]
            for is_flag, title, detail in rule_rows:
                if "Credible" in title:
                    icon, css = ("✓", "check-pass") if is_flag else ("⚠", "check-warn")
                else:
                    icon, css = ("⚠", "check-flag") if is_flag else ("✓", "check-pass")
                st.markdown(f"""
                <div class='breakdown-row'>
                  <span class='{css}'>{icon}</span>
                  <div>
                    <div style='color:{COLOR_TEXT};font-weight:600;font-size:0.88rem;'>{title}</div>
                    <div style='color:{COLOR_TEXT2};font-size:0.78rem;'>{detail}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style='border-top:1px solid {COLOR_BORDER};margin-top:0.8rem;padding-top:0.8rem;
                 display:flex;justify-content:space-between;align-items:center;'>
              <span style='color:{COLOR_TEXT2};font-weight:600;font-size:0.88rem;'>
                Overall Suspicion Score
              </span>
              <span style='color:{color};font-size:1.15rem;font-weight:800;'>{score} / 100</span>
            </div>
            """, unsafe_allow_html=True)

        # Text statistics row
        avg_wps = round(stats["total_words"] / max(stats["total_sentences"], 1), 1)
        grade   = readability.get("grade_level", "N/A")
        sc5     = st.columns(5)
        stat_items = [
            ("📝", "Word Count",         stats["total_words"]),
            ("📄", "Sentences",          stats["total_sentences"]),
            ("¶",  "Paragraphs",         stats["total_paragraphs"]),
            ("⟺", "Avg Words/Sentence", avg_wps),
            ("🎓", "Reading Level",      grade),
        ]
        for i, (icon, label, val) in enumerate(stat_items):
            with sc5[i]:
                st.markdown(f"""
                <div class="stat-mini">
                  <div style='font-size:1.1rem;'>{icon}</div>
                  <div style='color:{COLOR_TEXT};font-size:1.25rem;font-weight:700;
                       margin:0.15rem 0;'>{val}</div>
                  <div style='color:{COLOR_TEXT2};font-size:0.73rem;'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📊 Sentiment", "📈 Word Frequency", "📋 Report"])

        with tab1:
            s1, s2, s3 = st.columns(3)
            s1.markdown(
                f"<div class='mc' style='border-left:3px solid {COLOR_LOW};'>"
                f"<div class='mc-label'>Positive</div>"
                f"<div class='mc-value'>{sentiment['positive_pct']:.1f}%</div></div>",
                unsafe_allow_html=True)
            s2.markdown(
                f"<div class='mc' style='border-left:3px solid {COLOR_HIGH};'>"
                f"<div class='mc-label'>Negative</div>"
                f"<div class='mc-value'>{sentiment['negative_pct']:.1f}%</div></div>",
                unsafe_allow_html=True)
            s3.markdown(
                f"<div class='mc' style='border-left:3px solid {COLOR_MED};'>"
                f"<div class='mc-label'>Neutral</div>"
                f"<div class='mc-value'>{sentiment['neutral_pct']:.1f}%</div></div>",
                unsafe_allow_html=True)
            st.markdown(
                f"<p style='color:{COLOR_TEXT2};margin-top:1rem;'>"
                f"Reading Time: {rt['reading_time_str']}</p>",
                unsafe_allow_html=True)

        with tab2:
            if la["sorted_freq"]:
                pairs = normalize_word_freq_pairs(la["sorted_freq"][:15])
                if pairs:
                    df_f = pd.DataFrame(pairs, columns=["Word", "Count"])
                    fig_f = px.bar(df_f, x="Count", y="Word", orientation="h")
                    fig_f.update_layout(**plotly_dark_layout("Top 15 Words", 400))
                    fig_f.update_layout(yaxis={"categoryorder": "total ascending"})
                    fig_f.update_traces(marker_color=COLOR_ACCENT)
                    st.plotly_chart(fig_f, use_container_width=True, config=make_plotly_config())
            else:
                st.info("No word frequency data available.")

        with tab3:
            rep = build_full_report(
                "News Analysis", la["text"], stats,
                (score, verdict, color, reasons, details),
                readability, sentiment,
                la["sorted_freq"][:15] if la["sorted_freq"] else []
            )
            st.text_area("Full Report", rep, height=300)
            if st.button("Save Report"):
                save_report(
                    st.session_state.user_id,
                    f"Analysis_{datetime.datetime.now().strftime('%Y%m%d%H%M')}",
                    rep
                )
                st.success("Report saved.")
            st.download_button("⬇ Download TXT", rep, file_name="report.txt")

        st.info(
            "ℹ This tool uses keyword and rule-based analysis to flag structural and "
            "linguistic patterns. Results indicate credibility signals only — they do not "
            "fact-check or guarantee factual accuracy."
        )


# ══════════════════════════════════════════════════════════════════════════════
# TEXT PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def page_text_processing():
    st.markdown(f"""
    <div style='margin-bottom:1.4rem;'>
      <h1 style='color:{COLOR_TEXT};margin:0;font-size:1.75rem;font-weight:800;'>📝 Text Processing</h1>
      <p style='color:{COLOR_TEXT2};margin:0.3rem 0 0;font-size:0.88rem;'>
        Clean and format text using standard operations.
      </p>
    </div>
    """, unsafe_allow_html=True)

    text_input = st.text_area("Input Text", height=200)
    processed  = text_input

    c1, c2, c3 = st.columns(3)
    if c1.button("Clean Extra Spaces", use_container_width=True):
        processed = clean_extra_spaces(text_input)
    if c2.button("Remove Line Breaks", use_container_width=True):
        processed = clean_line_breaks(text_input)
    if c3.button("Sentence Case",      use_container_width=True):
        processed = format_sentence_case(text_input)

    st.text_area("Processed Text", processed, height=200)

    st.markdown("<br/>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"<h3 style='color:{COLOR_TEXT};margin-top:0;'>Search &amp; Replace</h3>",
                    unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns([2, 2, 1])
        with sc1: search  = st.text_input("Find")
        with sc2: replace = st.text_input("Replace with")
        with sc3:
            st.markdown("<br/>", unsafe_allow_html=True)
            do_rep = st.button("Replace", use_container_width=True)
        if do_rep and search:
            new_text, count = replace_word_in_text(processed, search, replace)
            st.success(f"Replaced {count} occurrence(s).")
            st.text_area("Result", new_text, height=150)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS (ANALYTICS)
# ══════════════════════════════════════════════════════════════════════════════
def page_analysis():
    st.markdown(f"""
    <div style='margin-bottom:1.4rem;'>
      <h1 style='color:{COLOR_TEXT};margin:0;font-size:1.75rem;font-weight:800;'>📈 Analytics</h1>
      <p style='color:{COLOR_TEXT2};margin:0.3rem 0 0;font-size:0.88rem;'>
        Explore patterns across all your analyzed texts.
      </p>
    </div>
    """, unsafe_allow_html=True)

    history = get_user_history(st.session_state.user_id, limit=200)
    if not history:
        st.markdown(
            f"<div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};"
            f"border-radius:12px;padding:3rem;text-align:center;color:{COLOR_TEXT2};'>"
            "No history available. Analyze some text first.</div>", unsafe_allow_html=True)
        return

    df_h = pd.DataFrame(history)
    c1, c2 = st.columns(2)

    with c1:
        vc = df_h["verdict"].value_counts().reset_index()
        vc.columns = ["Verdict", "Count"]
        fig = px.pie(
            vc, names="Verdict", values="Count", hole=0.6,
            color="Verdict",
            color_discrete_map={
                "LOW SUSPICION": COLOR_LOW,
                "NEEDS VERIFICATION": COLOR_MED,
                "HIGH SUSPICION": COLOR_HIGH
            }
        )
        fig.update_layout(**plotly_dark_layout("Suspicion Distribution", 340))
        st.plotly_chart(fig, use_container_width=True, config=make_plotly_config())

    with c2:
        df_h["date"] = pd.to_datetime(df_h["created_at"]).dt.date
        daily = df_h.groupby("date").size().reset_index(name="count")
        fig2  = px.line(daily, x="date", y="count")
        fig2.update_layout(**plotly_dark_layout("Activity Over Time", 340))
        fig2.update_traces(line_color=COLOR_ACCENT, fill="tozeroy",
                           fillcolor=f"rgba(56,189,248,0.07)")
        st.plotly_chart(fig2, use_container_width=True, config=make_plotly_config())

    st.markdown(f"<h3 style='color:{COLOR_TEXT};'>Results Distribution</h3>",
                unsafe_allow_html=True)
    vc_bar = df_h["verdict"].value_counts().reindex(
        ["LOW SUSPICION", "NEEDS VERIFICATION", "HIGH SUSPICION"], fill_value=0
    ).reset_index()
    vc_bar.columns = ["Verdict", "Count"]
    fig3 = px.bar(
        vc_bar, x="Count", y="Verdict", orientation="h", color="Verdict",
        color_discrete_map={
            "LOW SUSPICION": COLOR_LOW,
            "NEEDS VERIFICATION": COLOR_MED,
            "HIGH SUSPICION": COLOR_HIGH
        }
    )
    fig3.update_layout(**plotly_dark_layout("", 280))
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True, config=make_plotly_config())

    avg_s = df_h["score"].mean()
    max_s = df_h["score"].max()
    min_s = df_h["score"].min()
    a1, a2, a3 = st.columns(3)
    with a1: st.markdown(metric_card_html("Avg Trust Score", f"{avg_s:.1f}", COLOR_ACCENT), unsafe_allow_html=True)
    with a2: st.markdown(metric_card_html("Max Trust Score", max_s, COLOR_HIGH),            unsafe_allow_html=True)
    with a3: st.markdown(metric_card_html("Min Trust Score", min_s, COLOR_LOW),             unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
def page_comparison():
    st.markdown(f"""
    <div style='margin-bottom:1.4rem;'>
      <h1 style='color:{COLOR_TEXT};margin:0;font-size:1.75rem;font-weight:800;'>🔄 Text Comparison</h1>
      <p style='color:{COLOR_TEXT2};margin:0.3rem 0 0;font-size:0.88rem;'>
        Compare two pieces of text to identify similarities and differences.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: text_a = st.text_area("Article A", height=250)
    with c2: text_b = st.text_area("Article B", height=250)

    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        compare = st.button("Compare Texts", use_container_width=True)

    if compare and text_a.strip() and text_b.strip():
        res = compare_texts(text_a, text_b)
        sim_color = COLOR_LOW if res["similarity_pct"] >= 60 else (
                    COLOR_MED if res["similarity_pct"] >= 30 else COLOR_HIGH)
        st.markdown(f"""
        <div style='background:{COLOR_CARD};border:1px solid {sim_color};border-radius:12px;
             padding:1.5rem;text-align:center;margin:1rem 0;'>
          <div style='color:{COLOR_TEXT2};font-size:0.8rem;text-transform:uppercase;
               letter-spacing:0.08em;margin-bottom:0.3rem;'>Similarity</div>
          <div style='color:{sim_color};font-size:2.8rem;font-weight:900;'>
            {res["similarity_pct"]:.1f}%
          </div>
          <div style='color:{COLOR_TEXT2};font-size:0.85rem;'>{res["similarity_label"]}</div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(metric_card_html("Words in A", res["word_count_a"]), unsafe_allow_html=True)
        with r2:
            st.markdown(metric_card_html("Words in B", res["word_count_b"]), unsafe_allow_html=True)
        with r3:
            st.markdown(metric_card_html("Common Words", res["common_words_count"]), unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        with d1:
            st.markdown(
                f"<div class='mc'><div class='mc-label'>Unique to A ({res['unique_to_a_count']})</div>"
                f"<div style='color:{COLOR_TEXT2};font-size:0.82rem;margin-top:0.3rem;'>"
                f"{', '.join(list(res['unique_to_a'])[:20])}</div></div>",
                unsafe_allow_html=True)
        with d2:
            st.markdown(
                f"<div class='mc'><div class='mc-label'>Common Words ({res['common_words_count']})</div>"
                f"<div style='color:{COLOR_TEXT2};font-size:0.82rem;margin-top:0.3rem;'>"
                f"{', '.join(list(res['common_words'])[:20])}</div></div>",
                unsafe_allow_html=True)
    elif compare:
        st.warning("⚠ Please enter text in both fields before comparing.")


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown(f"<h2 style='color:{COLOR_TEXT};'>📜 Analysis History</h2>",
                unsafe_allow_html=True)

    col_s, col_f, col_e, col_c = st.columns([3, 2, 1, 1])
    with col_s:
        search_q = st.text_input("", placeholder="🔍 Search history...", label_visibility="collapsed")
    with col_f:
        filter_level = st.selectbox(
            "", ["All Levels", "Low Suspicion", "Medium Suspicion", "High Suspicion"],
            label_visibility="collapsed")

    history = get_user_history(st.session_state.user_id)
    if search_q:
        history = [h for h in history if search_q.lower() in h["text_preview"].lower()]
    if filter_level != "All Levels":
        vm = {"Low Suspicion": "LOW SUSPICION",
              "Medium Suspicion": "NEEDS VERIFICATION",
              "High Suspicion": "HIGH SUSPICION"}
        history = [h for h in history if h["verdict"] == vm.get(filter_level, "")]

    with col_e:
        if history:
            df_exp = pd.DataFrame(history)[["created_at","text_preview","score","verdict","word_count"]]
            df_exp.columns = ["Date","Text Preview","Trust Score","Suspicion Level","Word Count"]
            st.download_button("⬇ CSV", df_exp.to_csv(index=False),
                               "history.csv", "text/csv", use_container_width=True)
    with col_c:
        if st.button("🗑 Clear", use_container_width=True):
            if st.session_state.get("confirm_clear"):
                clear_user_history(st.session_state.user_id)
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.rerun()
    if st.session_state.get("confirm_clear"):
        st.warning("⚠ Click Clear again to confirm deletion of all history.")

    if history:
        h1, h2, h3, h4, h5 = st.columns([3, 1, 2, 1, 1])
        for col, lbl in zip([h1,h2,h3,h4,h5], ["Text Preview","Score","Suspicion Level","Words",""]):
            col.markdown(
                f"<div style='color:{COLOR_TEXT2};font-size:0.78rem;font-weight:600;"
                f"padding:0.3rem 0;border-bottom:1px solid {COLOR_BORDER};'>{lbl}</div>",
                unsafe_allow_html=True)
        for rec in history:
            vc    = verdict_color(rec["verdict"])
            badge = suspicion_badge(rec["verdict"])
            c1, c2, c3, c4, c5 = st.columns([3, 1, 2, 1, 1])
            with c1:
                st.markdown(
                    f"<div style='color:{COLOR_TEXT};font-size:0.84rem;padding:0.45rem 0;'>"
                    f"{rec['text_preview'][:65]}...</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f"<div style='color:{vc};font-weight:700;padding:0.45rem 0;'>{rec['score']}</div>",
                    unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='padding:0.45rem 0;'>{badge}</div>", unsafe_allow_html=True)
            with c4:
                st.markdown(
                    f"<div style='color:{COLOR_TEXT2};padding:0.45rem 0;'>{rec['word_count']}</div>",
                    unsafe_allow_html=True)
            with c5:
                if st.button("🗑", key=f"del_{rec['id']}"):
                    delete_analysis(st.session_state.user_id, rec["id"])
                    st.rerun()
    else:
        st.markdown(
            f"<div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};"
            f"border-radius:12px;padding:3rem;text-align:center;color:{COLOR_TEXT2};'>"
            "No history found. Start analyzing text to build your history!</div>",
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════════════════
def page_reports():
    st.markdown(f"<h2 style='color:{COLOR_TEXT};'>📄 Saved Reports</h2>",
                unsafe_allow_html=True)
    reports = get_user_reports(st.session_state.user_id)
    if reports:
        for r in reports:
            with st.container(border=True):
                st.markdown(
                    f"<div style='color:{COLOR_TEXT};font-weight:700;'>{r['report_name']}</div>"
                    f"<div style='color:{COLOR_TEXT2};font-size:0.8rem;'>{r['created_at']}</div>",
                    unsafe_allow_html=True)
                if st.button("Load Report", key=f"lr_{r['id']}"):
                    succ, content = get_report_content(st.session_state.user_id, r["id"])
                    if succ:
                        st.text_area("Content", content, height=200)
                        st.download_button("⬇ Download", content, file_name=f"{r['report_name']}.txt")
                    else:
                        st.error("Could not load report.")
    else:
        st.markdown(
            f"<div style='background:{COLOR_CARD};border:1px solid {COLOR_BORDER};"
            f"border-radius:12px;padding:2rem;text-align:center;color:{COLOR_TEXT2};'>"
            "No reports saved yet. Generate one in the Credibility Checker.</div>",
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown(f"<h2 style='color:{COLOR_TEXT};'>⚙️ Settings</h2>",
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(f"<h3 style='color:{COLOR_TEXT};margin-top:0;'>Profile</h3>",
                        unsafe_allow_html=True)
            new_name = st.text_input("Display Name", value=st.session_state.user_name)
            st.markdown(
                f"<div style='color:{COLOR_TEXT2};font-size:0.82rem;margin-bottom:0.5rem;'>"
                f"Email: {st.session_state.user_email}</div>",
                unsafe_allow_html=True)
            if st.button("Update Name"):
                ok, msg = update_user_name(st.session_state.user_id, new_name)
                if ok:
                    st.session_state.user_name = new_name
                    st.success("Name updated!")
                else:
                    st.error(msg)
    with c2:
        with st.container(border=True):
            st.markdown(f"<h3 style='color:{COLOR_TEXT};margin-top:0;'>Security</h3>",
                        unsafe_allow_html=True)
            old_pw = st.text_input("Current Password",     type="password")
            new_pw = st.text_input("New Password",         type="password")
            cnf_pw = st.text_input("Confirm New Password", type="password")
            if st.button("Change Password"):
                if new_pw != cnf_pw:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = change_password(st.session_state.user_id, old_pw, new_pw)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE ASSISTANT PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_assistant():
    st.markdown(f"""
    <div style='margin-bottom:1.4rem;'>
      <div style='display:flex; align-items:center; gap:0.7rem; margin-bottom:0.3rem;'>
        <span style='font-size:1.6rem;'>🤖</span>
        <h1 style='color:{COLOR_TEXT};margin:0;font-size:1.75rem;font-weight:800;'>
          Engine Assistant
        </h1>
        <span style="display:inline-block; background:rgba(56,189,248,0.12);
             border:1px solid rgba(56,189,248,0.3); border-radius:999px;
             padding:2px 12px; color:{COLOR_ACCENT}; font-size:0.68rem;
             font-weight:700; letter-spacing:0.06em;">KEYWORD-BASED</span>
      </div>
      <p style='color:{COLOR_TEXT2};margin:0;font-size:0.88rem;'>
        Ask questions about the project, text analysis, or your latest result.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message when empty
    if not st.session_state.assistant_messages:
        st.session_state.assistant_messages.append({
            "role": "assistant",
            "content": (
                "Hi! I'm the Engine Assistant 👋\n\n"
                "I can explain the project's features, detection rules, "
                "scores, and your latest analysis."
            )
        })

    # Display chat history
    for msg in st.session_state.assistant_messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Quick questions
    st.markdown(f"<div style='color:{COLOR_TEXT2};font-size:0.78rem;"
                f"margin:0.6rem 0 0.3rem;'>Suggested questions:</div>",
                unsafe_allow_html=True)
    qq1, qq2, qq3 = st.columns(3)
    quick_qs = [
        ("How is the score calculated?", qq1),
        ("What rules does the engine check?", qq2),
        ("Explain my latest result", qq3),
    ]
    for question, col in quick_qs:
        with col:
            if st.button(question, key=f"qq_{question[:20]}", use_container_width=True):
                st.session_state.assistant_messages.append({"role": "user", "content": question})
                st.session_state.assistant_messages.append({"role": "assistant", "content": _bot_reply(question)})
                st.rerun()

    # Chat input
    user_input = st.chat_input("Type your question here...")
    if user_input:
        st.session_state.assistant_messages.append({"role": "user", "content": user_input})
        st.session_state.assistant_messages.append({"role": "assistant", "content": _bot_reply(user_input)})
        st.rerun()

    # Clear chat button
    if st.session_state.assistant_messages:
        _, _, cc = st.columns([5, 5, 2])
        with cc:
            if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True, type="secondary"):
                st.session_state.assistant_messages = []
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    render_auth()
else:
    render_sidebar()
    page = st.session_state.current_page
    if   page == "Home":                page_home()
    elif page == "Dashboard":           page_dashboard()
    elif page == "Credibility Checker": page_credibility_checker()
    elif page == "Text Processing":     page_text_processing()
    elif page == "Analysis":            page_analysis()
    elif page == "Comparison":          page_comparison()
    elif page == "Engine Assistant":    page_assistant()
    elif page == "History":             page_history()
    elif page == "Reports":             page_reports()
    elif page == "Settings":            page_settings()
    else:                               page_home()