"""
================================================================================
Module: fake_news_detector.py
================================================================================
Python Concepts Demonstrated:
- Rule-Based Algorithms: Deterministic heuristic scoring without black-box ML
- Sets: Unique word sets and fast set intersection for keyword matching
- Dictionaries: Mapping categories, weights, and scoring thresholds
- Tuples: Returning immutable analysis results (score, verdict, color, reasons)
- Lists: Aggregating matched phrases and explanatory reasons
- Conditionals: 'if', 'elif', 'else' evaluating thresholds and scoring limits
- Loops: Iterating over phrases, characters, and word tokens
- String Operations: Lowercasing, sub-string searching, punctuation scanning
================================================================================
"""

import string
from utils.text_utils import tokenize_words


# Default fallback keywords if file or database is not loaded yet
DEFAULT_KEYWORDS = {
    "suspicious": [
        "shocking", "miracle", "secret", "exposed", "unbelievable",
        "conspiracy", "hoax", "cure", "banned", "censored", "bombshell",
        "coverup", "proof", "guaranteed", "illuminati", "alien",
        "hidden truth", "magic formula", "instant cure", "100% true", "leaked"
    ],
    "clickbait": [
        "you won't believe", "what happens next", "mind blown", "will shock you",
        "doctors hate this", "one weird trick", "see what happens", "must see",
        "gone viral", "unreal", "jaw dropping", "this is crazy",
        "stop everything", "act now", "before it gets deleted"
    ],
    "credible": [
        "according to", "spokesperson", "researchers", "published", "confirmed",
        "official", "statement", "reuters", "associated press", "study found",
        "investigation", "peer-reviewed", "data shows", "evidence suggests",
        "health organization", "university", "spokesman", "verified",
        "documented", "analysis shows", "press release", "conference"
    ]
}


def detect_clickbait_phrases(text: str, phrases: list) -> list:
    """
    Demonstrates: Lists, Loops, String operations.
    Searches for multi-word clickbait phrases in lowercased text.
    """
    lower_text = text.lower()
    matched_phrases = []

    for phrase in phrases:
        phrase_clean = phrase.strip().lower()
        if phrase_clean and phrase_clean in lower_text:
            matched_phrases.append(phrase_clean)

    return matched_phrases


def detect_suspicious_words(words_list: list, suspicious_keywords: list) -> list:
    """
    Demonstrates: Sets and Set Operations.
    Converts both collections into Sets to perform fast intersection matching.
    """
    # Create sets for O(1) average lookup time
    article_words_set = set(words_list)
    suspicious_set = set(k.lower() for k in suspicious_keywords)

    # Set intersection identifies common elements instantly
    matched_set = article_words_set.intersection(suspicious_set)
    return list(matched_set)


def detect_credible_words(words_list: list, credible_keywords: list, raw_text: str) -> list:
    """
    Demonstrates: Sets and Substring matching.
    Detects credible journalistic signals (both single words and multi-word phrases).
    """
    matched = set()
    lower_text = raw_text.lower()
    words_set = set(words_list)

    for item in credible_keywords:
        item_clean = item.strip().lower()
        if " " in item_clean:
            # Multi-word phrase check (e.g. "according to", "study found")
            if item_clean in lower_text:
                matched.add(item_clean)
        else:
            # Single word check
            if item_clean in words_set:
                matched.add(item_clean)

    return list(matched)


def check_excessive_punctuation(text: str) -> tuple:
    """
    Demonstrates: Loops, Conditionals, Tuples.
    Detects sensational punctuation patterns such as '!!!', '???', or '!?!?'.
    Returns a tuple: (cluster_count, boolean_flag)
    """
    patterns = ["!!", "??", "!?", "?!"]
    total_clusters = 0

    for pattern in patterns:
        total_clusters += text.count(pattern)

    is_excessive = total_clusters >= 2
    return (total_clusters, is_excessive)


def check_capitalization_ratio(raw_text: str) -> tuple:
    """
    Demonstrates: Loops, Lists, String methods, Floats, Tuples.
    Calculates the percentage of words written in ALL-CAPS (shouting style).
    Returns a tuple: (all_caps_count, total_words, ratio_percentage)
    """
    words = raw_text.split()
    if not words:
        return (0, 0, 0.0)

    all_caps_count = 0
    valid_word_count = 0

    for w in words:
        cleaned = w.strip(string.punctuation)
        # Only consider words with at least 2 letters to avoid counting 'I' or 'A'
        if len(cleaned) >= 2 and cleaned.isalpha():
            valid_word_count += 1
            if cleaned.isupper():
                all_caps_count += 1

    if valid_word_count == 0:
        return (0, 0, 0.0)

    ratio = round((all_caps_count / valid_word_count) * 100, 1)
    return (all_caps_count, valid_word_count, ratio)


def calculate_fake_news_score(
    text: str,
    keywords_dict: dict = None
) -> tuple:
    """
    Demonstrates:
    - Variables, Conditionals (if, elif, else), Dictionaries, Lists, Tuples
    - Transparent scoring heuristic algorithm (0 to 100 scale)
    
    Scoring Breakdown:
    - Base score: 10
    - Suspicious keywords: +12 points per word (max 40)
    - Clickbait phrases: +15 points per phrase (max 30)
    - Excessive punctuation (!!, ??): +10 to +15 points
    - High ALL-CAPS ratio (>15%): +15 points; (>30%): +25 points
    - Short content (<20 words): +10 points (unverified snippet penalty)
    - Credible words detected: -10 points each (reduces suspiciousness)
    
    Verdicts:
    - 0 to 35:   "Likely Reliable"       (Color: Green)
    - 36 to 65:  "Possibly Misleading"   (Color: Orange/Amber)
    - 66 to 100: "Suspicious / Fake"     (Color: Red)

    Returns:
    - Tuple: (final_score: int, verdict: str, color_hex: str, reasons_list: list, details_dict: dict)
    """
    if not text or not text.strip():
        return (
            0,
            "No Content",
            "#64748B",
            ["No text was provided for analysis."],
            {}
        )

    # Use default keywords if none provided
    if not keywords_dict:
        keywords_dict = DEFAULT_KEYWORDS

    suspicious_bank = keywords_dict.get("suspicious", DEFAULT_KEYWORDS["suspicious"])
    clickbait_bank = keywords_dict.get("clickbait", DEFAULT_KEYWORDS["clickbait"])
    credible_bank = keywords_dict.get("credible", DEFAULT_KEYWORDS["credible"])

    # Tokenize words for vocabulary checks
    words_lower = tokenize_words(text, keep_case=False)
    total_words = len(words_lower)

    # Rule 1: Suspicious Words Check
    matched_suspicious = detect_suspicious_words(words_lower, suspicious_bank)
    suspicious_points = min(len(matched_suspicious) * 12, 40)

    # Rule 2: Clickbait Phrases Check
    matched_clickbait = detect_clickbait_phrases(text, clickbait_bank)
    clickbait_points = min(len(matched_clickbait) * 15, 30)

    # Rule 3: Punctuation Patterns Check
    punct_clusters, is_punct_excessive = check_excessive_punctuation(text)
    punct_points = 0
    if punct_clusters >= 4:
        punct_points = 15
    elif punct_clusters >= 2:
        punct_points = 10

    # Rule 4: Capitalization / Shouting Check
    caps_count, valid_words, caps_ratio = check_capitalization_ratio(text)
    caps_points = 0
    if caps_ratio >= 30.0:
        caps_points = 25
    elif caps_ratio >= 15.0:
        caps_points = 15

    # Rule 5: Credible Journalistic Terms (Score Reducer)
    matched_credible = detect_credible_words(words_lower, credible_bank, text)
    credible_points_reduction = min(len(matched_credible) * 10, 30)

    # Rule 6: Very Short Article Check
    brevity_points = 0
    if 0 < total_words < 20:
        brevity_points = 10

    # Base initial score
    base_score = 10

    # Calculate raw score using addition and subtraction
    raw_score = (
        base_score
        + suspicious_points
        + clickbait_points
        + punct_points
        + caps_points
        + brevity_points
        - credible_points_reduction
    )

    # Clamp score between 0 and 100 using conditional statements
    if raw_score < 5:
        final_score = 5
    elif raw_score > 98:
        final_score = 98
    else:
        final_score = int(raw_score)

    # Determine Verdict and Color using if-elif-else
    if final_score <= 35:
        verdict = "Likely Reliable"
        color_hex = "#16A34A"  # Emerald Green
    elif final_score <= 65:
        verdict = "Possibly Misleading"
        color_hex = "#D97706"  # Amber / Warning
    else:
        verdict = "Suspicious / Likely Fake"
        color_hex = "#DC2626"  # Red

    # Generate student-friendly "Why this result?" explanation list
    reasons = []

    if matched_suspicious:
        reasons.append(
            f"Detected {len(matched_suspicious)} sensational keyword(s): "
            f"{', '.join(repr(w) for w in matched_suspicious[:5])} (+{suspicious_points} pts)"
        )
    else:
        reasons.append("No prominent sensational or conspiracy keywords detected.")

    if matched_clickbait:
        reasons.append(
            f"Detected {len(matched_clickbait)} clickbait phrase(s): "
            f"{', '.join(repr(p) for p in matched_clickbait[:3])} (+{clickbait_points} pts)"
        )

    if punct_points > 0:
        reasons.append(
            f"Excessive emotional punctuation detected: {punct_clusters} cluster(s) "
            f"like '!!' or '??' (+{punct_points} pts)"
        )

    if caps_points > 0:
        reasons.append(
            f"High capitalization detected: {caps_ratio}% of words in ALL-CAPS "
            f"({caps_count} words) (+{caps_points} pts)"
        )

    if brevity_points > 0:
        reasons.append(
            f"Text is very brief ({total_words} words); lacks sufficient journalistic context (+10 pts)"
        )

    if matched_credible:
        reasons.append(
            f"Contains credible journalistic attribution: "
            f"{', '.join(repr(c) for c in matched_credible[:4])} (-{credible_points_reduction} pts)"
        )
    else:
        reasons.append("No official attribution or journalistic sourcing indicators found.")

    details = {
        "score": final_score,
        "verdict": verdict,
        "color": color_hex,
        "suspicious_matches": matched_suspicious,
        "clickbait_matches": matched_clickbait,
        "credible_matches": matched_credible,
        "caps_ratio": caps_ratio,
        "punct_clusters": punct_clusters,
        "total_words": total_words
    }

    return (final_score, verdict, color_hex, reasons, details)
