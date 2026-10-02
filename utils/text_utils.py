"""
================================================================================
Module: text_utils.py (Part of 'utils' package)
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
    Demonstrates: String splitting, List comprehension/filtering, Conditionals.
    Counts non-empty paragraphs separated by newlines.
    """
    if not text or not text.strip():
        return 0
    lines = text.split("\n")
    non_empty = [line.strip() for line in lines if line.strip()]
    return len(non_empty)


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
            # Avoid duplicate reporting of the same repeated word pair
            repeated.append(words[i])

    return repeated


def get_word_frequencies(words_list: list) -> dict:
    """
    Demonstrates: Dictionaries, Loops, Conditionals.
    Counts occurrences of each word and returns a dictionary: {word: count}.
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


def replace_word_in_text(text: str, find_word: str, replace_with: str, case_sensitive: bool = False) -> tuple:
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
        # Case-insensitive replacement using word boundary scanning or simple approach
        # For beginner clarity: count matches ignoring case and replace
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
            if text[i : i + find_len].lower() == lower_find:
                result_chunks.append(replace_with)
                i += find_len
            else:
                result_chunks.append(text[i])
                i += 1

        return ("".join(result_chunks), occurrences)


def count_syllables_in_word(word: str) -> int:
    """
    Estimates syllable count for a word using vowel sequence rules.
    Used for calculating Flesch Reading Ease readability index.
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
    Formula: 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    """
    if not text or not text.strip():
        return {
            "score": 0.0,
            "reading_ease": "N/A",
            "grade_level": "N/A",
            "interpretation": "Enter text to calculate readability metrics."
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
            "interpretation": "No words detected."
        }

    total_syllables = sum(count_syllables_in_word(w) for w in words)

    asl = total_words / total_sentences                    # Average Sentence Length
    asw = total_syllables / total_words                   # Average Syllables per Word

    raw_flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
    score = round(max(0.0, min(100.0, raw_flesch)), 1)

    if score >= 90.0:
        ease = "Very Easy"
        grade = "5th Grade"
        interp = "Effortless to read; conversational and accessible to everyone."
    elif score >= 80.0:
        ease = "Easy"
        grade = "6th Grade"
        interp = "Conversational English; standard consumer reading level."
    elif score >= 70.0:
        ease = "Fairly Easy"
        grade = "7th Grade"
        interp = "Clear and plain English; easy for general audiences."
    elif score >= 60.0:
        ease = "Standard"
        grade = "8th - 9th Grade"
        interp = "Standard journalistic and modern publication reading level."
    elif score >= 50.0:
        ease = "Fairly Difficult"
        grade = "10th - 12th Grade"
        interp = "High school level; requires focused attention."
    elif score >= 30.0:
        ease = "Difficult"
        grade = "College Level"
        interp = "Academic or specialized reading level; complex syntax."
    else:
        ease = "Very Difficult"
        grade = "Graduate / Professional"
        interp = "Dense legal, scientific, or highly technical documentation."

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
    Estimates reading time (silent at 200 WPM) and speaking presentation time (verbal at 130 WPM).
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


def analyze_tone_sentiment(text: str) -> dict:
    """
    Rule-based emotional and stylistic tone distribution.
    Categorizes tone into Positive, Neutral/Objective, Negative, and Sensational.
    """
    if not text or not text.strip():
        return {
            "positive_pct": 0.0,
            "neutral_pct": 100.0,
            "negative_pct": 0.0,
            "sensational_pct": 0.0,
            "predominant_tone": "Neutral",
            "summary": "No text provided."
        }

    positive_lexicon = {
        "success", "growth", "breakthrough", "confirmed", "progress", "advance",
        "beneficial", "improvement", "positive", "opportunity", "efficient",
        "effective", "solution", "reliable", "trustworthy", "promising",
        "innovation", "thrive", "excellent", "achievement", "sustainable"
    }

    negative_lexicon = {
        "crisis", "failure", "danger", "collapse", "threat", "damage",
        "risk", "loss", "decline", "corrupt", "conflict", "problem",
        "adverse", "severe", "fatal", "harmful", "warning", "catastrophe"
    }

    sensational_lexicon = {
        "shocking", "bombshell", "miracle", "secret", "exposed", "unbelievable",
        "conspiracy", "hoax", "banned", "censored", "crazy", "mind blown",
        "unreal", "magic", "insane", "viral", "deleted", "guaranteed"
    }

    words = tokenize_words(text, keep_case=False)
    total_words = len(words)
    if total_words == 0:
        return {
            "positive_pct": 0.0,
            "neutral_pct": 100.0,
            "negative_pct": 0.0,
            "sensational_pct": 0.0,
            "predominant_tone": "Neutral",
            "summary": "Empty content."
        }

    pos_count = sum(1 for w in words if w in positive_lexicon)
    neg_count = sum(1 for w in words if w in negative_lexicon)
    sens_count = sum(1 for w in words if w in sensational_lexicon)

    emotional_words = pos_count + neg_count + sens_count
    neutral_words = max(0, total_words - emotional_words)

    pos_pct = round((pos_count / total_words) * 100, 1)
    neg_pct = round((neg_count / total_words) * 100, 1)
    sens_pct = round((sens_count / total_words) * 100, 1)
    neu_pct = round((neutral_words / total_words) * 100, 1)

    # Determine predominant tone
    scores = [
        ("Objective / Neutral", neu_pct),
        ("Positive", pos_pct),
        ("Negative / Critical", neg_pct),
        ("Sensational / Dramatic", sens_pct)
    ]
    scores.sort(key=lambda x: x[1], reverse=True)
    predominant = scores[0][0]

    return {
        "positive_pct": pos_pct,
        "neutral_pct": neu_pct,
        "negative_pct": neg_pct,
        "sensational_pct": sens_pct,
        "positive_count": pos_count,
        "negative_count": neg_count,
        "sensational_count": sens_count,
        "predominant_tone": predominant,
        "summary": f"Predominantly {predominant} with {neu_pct}% neutral/objective vocabulary."
    }


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

