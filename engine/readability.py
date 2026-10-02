"""
================================================================================
Module: readability.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- Functions with Return Values: Returning dictionaries with multiple metrics
- Loops: Iterating over characters to count syllables
- Conditionals: Classifying readability levels with if-elif-else chains
- Variables & Data Types: int, float, str used for calculations
- Exception Handling: Guarding against zero-division
- Mathematical Formulas: Flesch Reading Ease calculation
================================================================================
"""

import string
from engine.text_processor import tokenize_words, split_sentences


def count_syllables_in_word(word: str) -> int:
    """
    Estimates syllable count for a word using vowel sequence rules.
    Used for calculating the Flesch Reading Ease readability index.

    This is a SIMPLE rule-based estimator — not an NLP library.
    """
    word = word.lower().strip(string.punctuation)
    if not word:
        return 0
    if len(word) <= 3:
        return 1

    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    # Remove silent trailing 'e'
    if word.endswith("e") and not word.endswith("le") and len(word) > 2:
        if not (word.endswith("ee") or word.endswith("ye")):
            count -= 1

    return max(1, count)


def calculate_readability_score(text: str) -> dict:
    """
    Calculates the Flesch Reading Ease Score and Reading Grade Level.

    Formula: 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)

    This is a simple rule-based readability estimate.
    It does NOT use any NLP or ML library.
    """
    if not text or not text.strip():
        return {
            "score": 0.0,
            "reading_ease": "N/A",
            "grade_level": "N/A",
            "interpretation": "Enter text to calculate readability metrics.",
            "avg_sentence_length": 0.0,
            "avg_syllables_per_word": 0.0,
            "total_syllables": 0
        }

    words = tokenize_words(text, keep_case=False)
    sentences = split_sentences(text)

    total_words = len(words)
    total_sentences = max(1, len(sentences))

    if total_words == 0:
        return {
            "score": 0.0,
            "reading_ease": "N/A",
            "grade_level": "N/A",
            "interpretation": "No words detected.",
            "avg_sentence_length": 0.0,
            "avg_syllables_per_word": 0.0,
            "total_syllables": 0
        }

    total_syllables = sum(count_syllables_in_word(w) for w in words)

    # Average Sentence Length and Average Syllables per Word
    asl = total_words / total_sentences
    asw = total_syllables / total_words

    # Flesch Reading Ease formula
    raw_flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
    score = round(max(0.0, min(100.0, raw_flesch)), 1)

    # Classify readability using if-elif-else
    if score >= 90.0:
        ease = "Very Easy"
        grade = "5th Grade"
        interp = "Easy to Read — conversational and accessible to everyone."
    elif score >= 80.0:
        ease = "Easy"
        grade = "6th Grade"
        interp = "Easy to Read — standard consumer reading level."
    elif score >= 70.0:
        ease = "Fairly Easy"
        grade = "7th Grade"
        interp = "Easy to Read — clear and plain English."
    elif score >= 60.0:
        ease = "Moderate"
        grade = "8th - 9th Grade"
        interp = "Moderate — standard journalistic reading level."
    elif score >= 50.0:
        ease = "Fairly Difficult"
        grade = "10th - 12th Grade"
        interp = "Moderate — requires focused attention."
    elif score >= 30.0:
        ease = "Difficult"
        grade = "College Level"
        interp = "Difficult to Read — academic or specialized content."
    else:
        ease = "Very Difficult"
        grade = "Graduate / Professional"
        interp = "Difficult to Read — dense technical documentation."

    return {
        "score": score,
        "reading_ease": ease,
        "grade_level": grade,
        "interpretation": interp,
        "avg_sentence_length": round(asl, 1),
        "avg_syllables_per_word": round(asw, 2),
        "total_syllables": total_syllables
    }


def estimate_reading_time(total_words: int) -> dict:
    """
    Estimates reading time (silent at 200 WPM) and speaking time (130 WPM).
    Demonstrates: Variables, Conditionals, Arithmetic, Dictionaries.
    """
    if total_words <= 0:
        return {
            "reading_time_seconds": 0,
            "reading_time_str": "0 sec",
            "speaking_time_seconds": 0,
            "speaking_time_str": "0 sec"
        }

    # Silent reading @ 200 wpm
    read_secs = int((total_words / 200) * 60)
    read_mins = read_secs // 60
    read_rem_secs = read_secs % 60
    if read_mins > 0:
        read_str = f"{read_mins} min {read_rem_secs} sec"
    else:
        read_str = f"{max(1, read_secs)} sec"

    # Speaking @ 130 wpm
    speak_secs = int((total_words / 130) * 60)
    speak_mins = speak_secs // 60
    speak_rem_secs = speak_secs % 60
    if speak_mins > 0:
        speak_str = f"{speak_mins} min {speak_rem_secs} sec"
    else:
        speak_str = f"{max(1, speak_secs)} sec"

    return {
        "reading_time_seconds": read_secs,
        "reading_time_str": read_str,
        "speaking_time_seconds": speak_secs,
        "speaking_time_str": speak_str
    }
