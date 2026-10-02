"""
================================================================================
Module: text_processor.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- Strings & String Methods: strip, lower, upper, title, split, replace, count
- Lists: Storing tokens, sentences, and character lists
- Dictionaries: Storing word frequency counts {word: count}
- Sets: Identifying unique words and fast membership checking
- Tuples: Returning immutable pairs/results (e.g., shortest/longest word pair)
- Loops: 'for' loops iterating over characters and words
- Conditionals: 'if', 'elif', 'else' for character filtering and validation
- Exception Handling: 'try-except' for zero-division prevention
================================================================================
"""

import string


# ─────────────────────────────────────────────
# TEXT CLEANING FUNCTIONS
# ─────────────────────────────────────────────

def clean_extra_spaces(text: str) -> str:
    """
    Demonstrates: String manipulation and split/join operations.
    Removes redundant spaces, leading/trailing whitespace, and normalizes spacing.
    """
    if not text:
        return ""
    # split() without arguments splits by any consecutive whitespace
    words = text.split()
    return " ".join(words)


# Convenient alias
clean_text = clean_extra_spaces


def clean_line_breaks(text: str) -> str:
    """
    Normalizes excess consecutive blank lines to single line breaks.
    """
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = []
    prev_empty = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_empty:
                cleaned.append("")
                prev_empty = True
        else:
            cleaned.append(stripped)
            prev_empty = False
    return "\n".join(cleaned)


def format_sentence_case(text: str) -> str:
    """
    Capitalizes the first character of each sentence and lowercases the rest.
    """
    if not text:
        return ""
    sentences = split_sentences(text)
    if not sentences:
        return text
    formatted = []
    for s in sentences:
        s_clean = s.strip()
        if s_clean:
            formatted.append(s_clean[0].upper() + s_clean[1:].lower())
    return " ".join(formatted)


# ─────────────────────────────────────────────
# TOKENIZATION & SPLITTING
# ─────────────────────────────────────────────

def tokenize_words(text: str, keep_case: bool = False) -> list:
    """
    Demonstrates: Lists, Loops, Conditionals, and String operations.
    Breaks a text string into a list of cleaned words, stripping punctuation.
    """
    if not text or not text.strip():
        return []

    # Standard punctuation set to strip from word edges
    punctuation_chars = string.punctuation

    raw_words = text.split()
    cleaned_words = []

    for raw_word in raw_words:
        # Strip punctuation from both ends of each word
        word = raw_word.strip(punctuation_chars)
        if word:
            if not keep_case:
                word = word.lower()
            cleaned_words.append(word)

    return cleaned_words


def split_sentences(text: str) -> list:
    """
    Demonstrates: Loops, Lists, String manipulation.
    Splits text into individual sentences based on standard terminators (. ! ?).
    """
    if not text or not text.strip():
        return []

    sentences = []
    current_sentence = []

    # Using a tuple of sentence terminators
    terminators = (".", "!", "?")

    for char in text:
        current_sentence.append(char)
        if char in terminators:
            sentence_str = "".join(current_sentence).strip()
            if sentence_str:
                sentences.append(sentence_str)
            current_sentence = []

    # Check if there is trailing text without a terminator
    remaining = "".join(current_sentence).strip()
    if remaining:
        sentences.append(remaining)

    return sentences


def count_paragraphs(text: str) -> int:
    """
    Demonstrates: String splitting, List filtering, Conditionals.
    Counts non-empty paragraphs separated by newlines.
    """
    if not text or not text.strip():
        return 0
    lines = text.split("\n")
    non_empty = [line.strip() for line in lines if line.strip()]
    return len(non_empty)


# ─────────────────────────────────────────────
# WORD ANALYSIS
# ─────────────────────────────────────────────

def find_repeated_adjacent_words(text: str) -> list:
    """
    Demonstrates: Lists, Loops, Range indexing, Conditionals.
    Detects repeated adjacent words (e.g., 'the the' or 'very very').
    Returns a list of repeated word strings.
    """
    words = tokenize_words(text, keep_case=False)
    repeated = []

    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            repeated.append(words[i])

    return repeated


def get_word_frequencies(words_list: list) -> dict:
    """
    Demonstrates: Dictionaries, Loops, Conditionals.
    Counts occurrences of each word and returns a dictionary: {word: count}.
    Does NOT use Counter or any advanced library — pure manual counting.
    """
    frequencies = {}

    for word in words_list:
        if word in frequencies:
            frequencies[word] += 1
        else:
            frequencies[word] = 1

    return frequencies


def find_longest_and_shortest_words(words_list: list) -> tuple:
    """
    Demonstrates: Tuples, Loops, Variables, Conditionals.
    Finds the longest and shortest words from a list of words.
    Returns a tuple: (shortest_word, longest_word).
    """
    if not words_list:
        return ("", "")

    shortest = words_list[0]
    longest = words_list[0]

    for word in words_list:
        if len(word) < len(shortest):
            shortest = word
        if len(word) > len(longest):
            longest = word

    # Returning an immutable tuple
    return (shortest, longest)


# ─────────────────────────────────────────────
# COMPREHENSIVE TEXT STATISTICS
# ─────────────────────────────────────────────

def calculate_text_statistics(text: str) -> dict:
    """
    Demonstrates:
    - Multiple data types: int, float, str, list, set, dict, tuple
    - Exception handling: try-except handling ZeroDivisionError
    - Comprehensive data aggregation into a dictionary
    """
    if not text or not text.strip():
        return {
            "total_words": 0,
            "unique_words": 0,
            "characters_with_spaces": 0,
            "characters_without_spaces": 0,
            "total_sentences": 0,
            "total_paragraphs": 0,
            "average_word_length": 0.0,
            "uppercase_words_count": 0,
            "punctuation_count": 0,
            "special_characters_count": 0,
            "shortest_word": "N/A",
            "longest_word": "N/A",
            "repeated_adjacent_words": []
        }

    # Tokenize words in both case formats
    words_lower = tokenize_words(text, keep_case=False)
    raw_words = text.split()

    # Total and unique word calculations using Sets
    total_words = len(words_lower)
    unique_words_set = set(words_lower)
    unique_words_count = len(unique_words_set)

    # Character counts
    chars_with_spaces = len(text)
    chars_without_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))

    # Sentence and paragraph counts
    sentences = split_sentences(text)
    total_sentences = len(sentences)
    total_paragraphs = count_paragraphs(text)

    # Calculate average word length using try-except to guard against ZeroDivisionError
    total_letters = sum(len(word) for word in words_lower)
    try:
        avg_word_len = round(total_letters / total_words, 2)
    except ZeroDivisionError:
        avg_word_len = 0.0

    # Count ALL-CAPS words (words with length > 1 in uppercase)
    uppercase_words = 0
    for w in raw_words:
        stripped = w.strip(string.punctuation)
        if len(stripped) > 1 and stripped.isupper():
            uppercase_words += 1

    # Punctuation and special character counts
    punctuation_count = 0
    special_char_count = 0
    standard_punctuation = set(string.punctuation)

    for ch in text:
        if ch in standard_punctuation:
            punctuation_count += 1
        elif not ch.isalnum() and not ch.isspace():
            special_char_count += 1

    # Longest and Shortest words tuple
    shortest, longest = find_longest_and_shortest_words(words_lower)

    # Repeated adjacent words
    repeated_words = find_repeated_adjacent_words(text)

    return {
        "total_words": total_words,
        "unique_words": unique_words_count,
        "characters_with_spaces": chars_with_spaces,
        "characters_without_spaces": chars_without_spaces,
        "total_sentences": total_sentences,
        "total_paragraphs": total_paragraphs,
        "average_word_length": avg_word_len,
        "uppercase_words_count": uppercase_words,
        "punctuation_count": punctuation_count,
        "special_characters_count": special_char_count,
        "shortest_word": shortest if shortest else "N/A",
        "longest_word": longest if longest else "N/A",
        "repeated_adjacent_words": repeated_words
    }
