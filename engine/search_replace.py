"""
================================================================================
Module: search_replace.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- Linear Search Algorithm: Sequential word-by-word searching
- String Operations: Case-insensitive matching, substring replacement
- Tuples: Returning (count, positions) pairs
- Lists: Storing matched indices
- Loops: Iterating over word tokens with enumerate()
- Conditionals: Handling empty input and case sensitivity
================================================================================
"""

from engine.text_processor import tokenize_words


def search_word_occurrences(text: str, target_word: str) -> tuple:
    """
    Demonstrates: Linear searching, Strings, Tuples, Lists.
    Searches for a specific word in the text (case-insensitive).
    Returns a tuple: (occurrences_count, list_of_matching_positions)
    """
    if not text or not target_word:
        return (0, [])

    words = tokenize_words(text, keep_case=False)
    target = target_word.strip().lower()

    count = 0
    matched_indices = []

    # Linear search through the list of words
    for index, word in enumerate(words):
        if word == target:
            count += 1
            matched_indices.append(index)

    return (count, matched_indices)


def replace_word_in_text(text: str, find_word: str, replace_with: str,
                         case_sensitive: bool = False) -> tuple:
    """
    Demonstrates: String replacement, Conditionals, Tuples.
    Replaces occurrences of find_word with replace_with.
    Returns a tuple: (updated_text, number_of_replacements).
    """
    if not text or not find_word:
        return (text, 0)

    if case_sensitive:
        occurrences = text.count(find_word)
        updated_text = text.replace(find_word, replace_with)
        return (updated_text, occurrences)
    else:
        # Case-insensitive replacement
        lower_text = text.lower()
        lower_find = find_word.lower()
        occurrences = lower_text.count(lower_find)

        if occurrences == 0:
            return (text, 0)

        # Build replacement maintaining non-matched characters
        # Simple iterative replacement for student readability
        result_chunks = []
        i = 0
        text_len = len(text)
        find_len = len(find_word)

        while i < text_len:
            if text[i: i + find_len].lower() == lower_find:
                result_chunks.append(replace_with)
                i += find_len
            else:
                result_chunks.append(text[i])
                i += 1

        return ("".join(result_chunks), occurrences)
