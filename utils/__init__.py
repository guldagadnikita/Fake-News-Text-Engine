"""
================================================================================
Package: utils
================================================================================
Concept Demonstrated: Python Packages
A package is a directory containing an '__init__.py' file and one or more Python
modules. It allows organizing related modules into a single namespace.

This package contains:
- text_utils.py: Functions for text processing, tokenization, and counting.
- sorting_utils.py: Manual sorting algorithm (Bubble Sort) and complexity helpers.
================================================================================
"""

# Exposing key functions from package modules for convenient access
from utils.text_utils import (
    clean_text,
    tokenize_words,
    split_sentences,
    get_word_frequencies,
    calculate_text_statistics,
    find_repeated_adjacent_words,
    search_word_occurrences,
    replace_word_in_text,
    clean_extra_spaces,
    calculate_readability_score,
    estimate_reading_time,
    analyze_tone_sentiment,
    format_sentence_case,
    clean_line_breaks
)

from utils.sorting_utils import (
    bubble_sort_frequencies,
    get_bubble_sort_explanation
)

__all__ = [
    "clean_text",
    "tokenize_words",
    "split_sentences",
    "get_word_frequencies",
    "calculate_text_statistics",
    "find_repeated_adjacent_words",
    "search_word_occurrences",
    "replace_word_in_text",
    "clean_extra_spaces",
    "calculate_readability_score",
    "estimate_reading_time",
    "analyze_tone_sentiment",
    "format_sentence_case",
    "clean_line_breaks",
    "bubble_sort_frequencies",
    "get_bubble_sort_explanation"
]
