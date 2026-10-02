"""
================================================================================
Package: engine
================================================================================
Concept Demonstrated: Python Packages

A package is a directory containing an '__init__.py' file and one or more Python
modules. It allows organizing related modules into a single namespace.

This package contains:
- text_processor.py   : Text statistics, tokenization, word frequency, cleaning
- fake_news_detector.py : Rule-based suspicious content scoring
- sorting_utils.py    : Manual Bubble Sort algorithm implementation
- search_replace.py   : Word searching and text replacement
- file_handler.py     : File reading, writing, and word list loading
- readability.py      : Flesch Reading Ease and reading time estimation
- sentiment.py        : Keyword-based positive/negative word analysis
- comparison.py       : Text comparison using set operations
- report_generator.py : Professional text report generation
================================================================================
"""

# Exposing key functions from package modules for convenient access
from engine.text_processor import (
    clean_text,
    clean_extra_spaces,
    clean_line_breaks,
    format_sentence_case,
    tokenize_words,
    split_sentences,
    count_paragraphs,
    get_word_frequencies,
    calculate_text_statistics,
    find_repeated_adjacent_words,
    find_longest_and_shortest_words,
)

from engine.sorting_utils import (
    bubble_sort_frequencies,
    bubble_sort_words_alphabetical,
    get_bubble_sort_explanation,
)

from engine.fake_news_detector import (
    calculate_fake_news_score,
    detect_suspicious_words,
    detect_clickbait_phrases,
    detect_credible_words,
    check_excessive_punctuation,
    check_capitalization_ratio,
)

from engine.search_replace import (
    search_word_occurrences,
    replace_word_in_text,
)

from engine.file_handler import (
    load_word_list,
    load_keywords_from_file,
    read_text_file,
    write_text_file,
)

from engine.readability import (
    calculate_readability_score,
    estimate_reading_time,
    count_syllables_in_word,
)

from engine.sentiment import (
    analyze_sentiment,
)

from engine.comparison import (
    compare_texts,
)

from engine.report_generator import (
    build_full_report,
)

__all__ = [
    "clean_text", "clean_extra_spaces", "clean_line_breaks",
    "format_sentence_case", "tokenize_words", "split_sentences",
    "count_paragraphs", "get_word_frequencies", "calculate_text_statistics",
    "find_repeated_adjacent_words", "find_longest_and_shortest_words",
    "bubble_sort_frequencies", "bubble_sort_words_alphabetical",
    "get_bubble_sort_explanation",
    "calculate_fake_news_score", "detect_suspicious_words",
    "detect_clickbait_phrases", "detect_credible_words",
    "check_excessive_punctuation", "check_capitalization_ratio",
    "search_word_occurrences", "replace_word_in_text",
    "load_word_list", "load_keywords_from_file",
    "read_text_file", "write_text_file",
    "calculate_readability_score", "estimate_reading_time",
    "count_syllables_in_word",
    "analyze_sentiment",
    "compare_texts",
    "build_full_report",
]
