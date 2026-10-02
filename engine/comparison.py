"""
================================================================================
Module: comparison.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- Sets: Set intersection, difference, and union for comparing text
- Dictionaries: Returning structured comparison results
- Functions with Return Values: Returning comprehensive comparison data
- Variables & Data Types: Counting and percentage calculations
- Conditionals: Classifying similarity levels
- Exception Handling: Division by zero guarding
================================================================================
"""

from engine.text_processor import tokenize_words


def compare_texts(text_a: str, text_b: str) -> dict:
    """
    Compares two pieces of text and returns detailed comparison metrics.

    Uses SET OPERATIONS to find:
    - Common words (intersection)
    - Words unique to Text A (difference)
    - Words unique to Text B (difference)
    - Similarity percentage based on Jaccard similarity

    Demonstrates: Sets, Dictionaries, Conditionals, Exception Handling.
    """
    # Handle empty inputs
    if not text_a or not text_a.strip():
        text_a = ""
    if not text_b or not text_b.strip():
        text_b = ""

    # Tokenize both texts
    words_a = tokenize_words(text_a, keep_case=False)
    words_b = tokenize_words(text_b, keep_case=False)

    # Word counts
    count_a = len(words_a)
    count_b = len(words_b)
    word_count_diff = abs(count_a - count_b)

    # Create SETS for set operations
    set_a = set(words_a)
    set_b = set(words_b)

    # Set operations — demonstrating union, intersection, difference
    common_words = set_a.intersection(set_b)       # Words in BOTH texts
    unique_to_a = set_a.difference(set_b)           # Words ONLY in Text A
    unique_to_b = set_b.difference(set_a)           # Words ONLY in Text B
    all_words = set_a.union(set_b)                  # ALL unique words combined

    # Calculate Jaccard Similarity (simple and explainable)
    # Similarity = |A ∩ B| / |A ∪ B| × 100
    try:
        similarity_pct = round((len(common_words) / len(all_words)) * 100, 1)
    except ZeroDivisionError:
        similarity_pct = 0.0

    # Classify similarity using conditionals
    if similarity_pct >= 80:
        similarity_label = "Very Similar"
    elif similarity_pct >= 50:
        similarity_label = "Moderately Similar"
    elif similarity_pct >= 20:
        similarity_label = "Somewhat Similar"
    else:
        similarity_label = "Very Different"

    return {
        "word_count_a": count_a,
        "word_count_b": count_b,
        "word_count_diff": word_count_diff,
        "unique_words_a": len(set_a),
        "unique_words_b": len(set_b),
        "common_words": sorted(list(common_words)),
        "common_words_count": len(common_words),
        "unique_to_a": sorted(list(unique_to_a)),
        "unique_to_a_count": len(unique_to_a),
        "unique_to_b": sorted(list(unique_to_b)),
        "unique_to_b_count": len(unique_to_b),
        "similarity_pct": similarity_pct,
        "similarity_label": similarity_label
    }
