"""
================================================================================
Module: sentiment.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- Sets: Fast keyword membership checking with O(1) lookups
- Dictionaries: Returning structured analysis results
- Lists: Storing matched positive/negative words
- Loops: Iterating over words to classify sentiment
- Conditionals: Determining predominant tone
- File Handling: Loading word lists from external files
- Functions with Default Arguments: Fallback word lists
================================================================================
"""

import os
from engine.text_processor import tokenize_words


# ─────────────────────────────────────────────
# DEFAULT WORD LISTS (fallback if files not found)
# ─────────────────────────────────────────────

DEFAULT_POSITIVE_WORDS = {
    "good", "great", "success", "successful", "happy", "safe", "safety",
    "progress", "benefit", "beneficial", "excellent", "positive", "growth",
    "breakthrough", "confirmed", "advance", "advanced", "improvement",
    "improved", "opportunity", "efficient", "effective", "solution",
    "reliable", "trustworthy", "promising", "innovation", "thrive",
    "achievement", "sustainable", "wonderful", "fantastic", "brilliant",
    "outstanding", "remarkable", "helpful", "support", "supported",
    "secure", "stable", "recovery", "recovered", "win", "won", "gain",
    "gained", "boost", "boosted", "strong", "strength", "healthy",
    "welcome", "welcomed", "praise", "praised", "approve", "approved",
    "agreement", "cooperation", "resolved", "resolution", "hope",
    "hopeful", "encouraging", "favorable", "favourable", "upgrade",
    "upgraded", "advisory", "precaution", "precautions", "prepared",
    "readiness", "assist", "assistance", "relief", "rescue", "rescued"
}

DEFAULT_NEGATIVE_WORDS = {
    "bad", "danger", "dangerous", "failure", "failed", "warning",
    "crisis", "problem", "problems", "risk", "risky", "loss", "lost",
    "decline", "declined", "corrupt", "corruption", "conflict", "adverse",
    "severe", "fatal", "harmful", "harm", "catastrophe", "threat",
    "threatened", "damage", "damaged", "collapse", "collapsed",
    "terrible", "horrible", "disaster", "tragic", "devastating",
    "alarming", "disturbing", "frightening", "dreadful", "awful",
    "miserable", "emergency", "flood", "flooding", "storm", "cyclone",
    "casualty", "casualties", "injured", "injury", "death", "deaths",
    "died", "killed", "destroyed", "destruction", "chaos", "panic",
    "outbreak", "shortage", "delay", "delayed", "disrupt", "disrupted",
    "disruption", "suspend", "suspended", "cancel", "cancelled",
    "worsen", "worsened", "worsening", "unrest", "protest", "protests",
    "controversy", "scandal", "fraud", "illegal", "violation", "victim",
    "victims", "suffer", "suffered", "suffering"
}


def load_word_list(file_path: str) -> set:
    """
    Loads a simple word list from a text file (one word/phrase per line).
    Demonstrates: File handling, Sets, Exception handling.
    Returns a set of lowercase words.
    """
    words = set()
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        words.add(line.lower())
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        pass  # Silently fall back to defaults
    return words


def analyze_sentiment(text: str, positive_words: set = None,
                      negative_words: set = None) -> dict:
    """
    Simple keyword-based sentiment/tone analysis.

    This is NOT machine learning or NLP — it is purely keyword-based.
    It counts positive and negative words from predefined lists.

    Demonstrates: Sets, Dictionaries, Loops, Conditionals.
    """
    if not text or not text.strip():
        return {
            "positive_count": 0,
            "negative_count": 0,
            "positive_words_found": [],
            "negative_words_found": [],
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 100.0,
            "predominant_tone": "Neutral",
            "result": "Neutral Language",
            "summary": "No text provided for analysis."
        }

    # Use defaults if no custom lists provided
    if positive_words is None:
        positive_words = DEFAULT_POSITIVE_WORDS
    if negative_words is None:
        negative_words = DEFAULT_NEGATIVE_WORDS

    words = tokenize_words(text, keep_case=False)
    total_words = len(words)

    if total_words == 0:
        return {
            "positive_count": 0,
            "negative_count": 0,
            "positive_words_found": [],
            "negative_words_found": [],
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 100.0,
            "predominant_tone": "Neutral",
            "result": "Neutral Language",
            "summary": "No words detected."
        }

    # Count positive and negative words
    pos_found = []
    neg_found = []

    for word in words:
        if word in positive_words:
            pos_found.append(word)
        elif word in negative_words:
            neg_found.append(word)

    pos_count = len(pos_found)
    neg_count = len(neg_found)
    neutral_count = total_words - pos_count - neg_count

    # Calculate percentages
    pos_pct = round((pos_count / total_words) * 100, 1)
    neg_pct = round((neg_count / total_words) * 100, 1)
    neu_pct = round((neutral_count / total_words) * 100, 1)

    # Determine result using conditionals
    if pos_count > neg_count:
        result = "Mostly Positive Language"
        tone = "Positive"
    elif neg_count > pos_count:
        result = "Mostly Negative Language"
        tone = "Negative"
    else:
        result = "Neutral Language"
        tone = "Neutral"

    return {
        "positive_count": pos_count,
        "negative_count": neg_count,
        "positive_words_found": list(set(pos_found)),
        "negative_words_found": list(set(neg_found)),
        "positive_pct": pos_pct,
        "negative_pct": neg_pct,
        "neutral_pct": neu_pct,
        "predominant_tone": tone,
        "result": result,
        "summary": f"Positive words: {pos_count} | Negative words: {neg_count} | "
                   f"Result: {result}"
    }
