"""
================================================================================
Test Suite: test_engine.py
================================================================================
Automated verification script for:
- Text utilities (stats, frequencies, search/replace)
- Manual Bubble Sort algorithm mechanics
- Rule-based fake news scoring logic
- MySQL Database connection, schema creation, and CRUD operations
- File handling functions
================================================================================
"""

import os
import sys

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from utils.text_utils import (
    calculate_text_statistics,
    tokenize_words,
    get_word_frequencies,
    search_word_occurrences,
    replace_word_in_text,
    clean_extra_spaces
)
from utils.sorting_utils import (
    bubble_sort_frequencies,
    bubble_sort_words_alphabetical
)
from fake_news_detector import calculate_fake_news_score
from database import DatabaseManager
from file_handler import load_keywords_from_file, read_text_file, write_text_file


def test_text_utils():
    print("\n--- [1/5] Testing Text Utilities ---")
    test_text = "The quick brown fox jumps over the lazy dog. The the dog was sleeping! Is this unbelievable?"

    # 1. Statistics
    stats = calculate_text_statistics(test_text)
    assert stats["total_words"] == 17, f"Expected 17 words, got {stats['total_words']}"
    assert stats["total_sentences"] == 3, f"Expected 3 sentences, got {stats['total_sentences']}"
    assert stats["repeated_adjacent_words"] == ["the"], f"Expected ['the'], got {stats['repeated_adjacent_words']}"
    assert stats["average_word_length"] > 0, "Average word length should be > 0"
    print("[OK] calculate_text_statistics passed")

    # 2. Search & Replace
    count, indices = search_word_occurrences(test_text, "the")
    assert count == 4, f"Expected 4 occurrences of 'the', got {count}"
    print("[OK] search_word_occurrences passed")

    replaced_text, rep_count = replace_word_in_text(test_text, "dog", "cat")
    assert rep_count == 2, f"Expected 2 replacements, got {rep_count}"
    assert "cat" in replaced_text, "Replacement word 'cat' not found in text"
    print("[OK] replace_word_in_text passed")

    # 3. Clean spaces
    messy_spaces = "  Hello    world!   This   is   Python.  "
    cleaned = clean_extra_spaces(messy_spaces)
    assert cleaned == "Hello world! This is Python.", f"Unexpected cleaned string: '{cleaned}'"
    print("[OK] clean_extra_spaces passed")


def test_sorting_utils():
    print("\n--- [2/5] Testing Manual Bubble Sort Algorithm ---")
    freq_data = [("apple", 2), ("banana", 5), ("cherry", 1), ("date", 9), ("elderberry", 5)]

    # 1. Sort descending by frequency
    sorted_items, passes, comparisons, swaps = bubble_sort_frequencies(freq_data, descending=True)
    counts = [item[1] for item in sorted_items]
    assert counts == [9, 5, 5, 2, 1], f"Expected [9, 5, 5, 2, 1], got {counts}"
    assert passes > 0, "Passes count should be > 0"
    assert comparisons > 0, "Comparisons count should be > 0"
    assert swaps > 0, "Swaps count should be > 0"
    print(f"✓ bubble_sort_frequencies (descending) passed: {passes} passes, {comparisons} comparisons, {swaps} swaps")

    # 2. Sort already sorted list to test O(n) early termination optimization
    already_sorted = [("a", 10), ("b", 8), ("c", 6), ("d", 4), ("e", 2)]
    sorted_res, passes_fast, comps_fast, swaps_fast = bubble_sort_frequencies(already_sorted, descending=True)
    assert passes_fast == 1, f"Expected 1 pass on already sorted list (early exit), got {passes_fast}"
    assert swaps_fast == 0, f"Expected 0 swaps on already sorted list, got {swaps_fast}"
    print("[OK] Bubble sort O(n) early break optimization verified")


def test_fake_news_detector():
    print("\n--- [3/5] Testing Rule-Based Fake News Heuristics ---")
    reliable_text = """According to official statements released by researchers at the university, 
    published data shows confirmed growth in solar energy. The spokesperson confirmed the findings."""

    score_rel, verdict_rel, color_rel, reasons_rel, _ = calculate_fake_news_score(reliable_text)
    assert score_rel <= 35, f"Expected low score for reliable text, got {score_rel}"
    assert verdict_rel == "Likely Reliable", f"Expected 'Likely Reliable', got '{verdict_rel}'"
    print(f"[OK] Reliable news scoring passed: Score = {score_rel} ({verdict_rel})")

    suspicious_text = """SHOCKING BOMBSHELL DISCOVERY! Secret miracle cure they don't want you to know about! 
    Doctors hate this one weird trick! Unbelievable hidden truth exposed! Act now before it gets deleted! Mind blown!"""

    score_sus, verdict_sus, color_sus, reasons_sus, _ = calculate_fake_news_score(suspicious_text)
    assert score_sus >= 66, f"Expected high score for suspicious text, got {score_sus}"
    assert verdict_sus == "Suspicious / Likely Fake", f"Expected 'Suspicious / Likely Fake', got '{verdict_sus}'"
    assert len(reasons_sus) >= 3, "Expected multiple reasons for suspicious text"
    print(f"[OK] Suspicious news scoring passed: Score = {score_sus} ({verdict_sus})")


def test_database_manager():
    print("\n--- [4/5] Testing MySQL Database CRUD Operations ---")
    db = DatabaseManager(host="localhost", user="root", password="root", database="fake_news_db")

    # 1. Connection & Init
    conn_ok, conn_msg = db.test_connection()
    assert conn_ok, f"MySQL connection failed: {conn_msg}"
    print("[OK] MySQL server reachable")

    init_ok, init_msg = db.initialize_database()
    assert init_ok, f"Database init failed: {init_msg}"
    print("[OK] fake_news_db and tables initialized successfully")

    # 2. Save Analysis (INSERT)
    save_ok, record_id = db.save_analysis(
        title="Automated Test Article",
        full_text="This is a test article for automated verification of MySQL integration.",
        total_words=11,
        total_sentences=1,
        avg_word_length=5.1,
        score=20,
        verdict="Likely Reliable",
        reasons_list=["Test reason 1", "Test reason 2"]
    )
    assert save_ok, f"Save analysis failed: {record_id}"
    print(f"✓ Inserted test record into MySQL: ID #{record_id}")

    # 3. Read Analysis (SELECT)
    fetch_ok, record = db.get_history_by_id(record_id)
    assert fetch_ok, f"Fetch record failed: {record}"
    assert record["title"] == "Automated Test Article", f"Title mismatch: {record['title']}"
    assert record["total_words"] == 11, f"Word count mismatch: {record['total_words']}"
    print("[OK] SELECT by ID verified")

    # 4. Filter Query (SELECT with WHERE)
    filter_ok, records = db.get_all_history(filter_verdict="Likely Reliable")
    assert filter_ok, "Filter query failed"
    assert any(r["id"] == record_id for r in records), "Inserted record not found in filtered list"
    print("[OK] SELECT with WHERE filtering verified")

    # 5. Delete (DELETE)
    del_ok, del_msg = db.delete_history_by_id(record_id)
    assert del_ok, f"Delete failed: {del_msg}"
    print(f"[OK] DELETE record #{record_id} verified")


def test_file_handler():
    print("\n--- [5/5] Testing File Handling ---")
    kw_path = os.path.join(PROJECT_DIR, "data", "keywords.txt")
    success, kw_dict = load_keywords_from_file(kw_path)
    assert success, f"Failed to load keywords: {kw_dict}"
    assert "suspicious" in kw_dict and len(kw_dict["suspicious"]) > 0, "Missing suspicious keywords"
    assert "clickbait" in kw_dict and len(kw_dict["clickbait"]) > 0, "Missing clickbait phrases"
    assert "credible" in kw_dict and len(kw_dict["credible"]) > 0, "Missing credible words"
    print(f"[OK] Loaded {len(kw_dict['suspicious'])} suspicious, {len(kw_dict['clickbait'])} clickbait, and {len(kw_dict['credible'])} credible keywords from file")

    # Temp file test
    test_file = os.path.join(PROJECT_DIR, "data", "temp_test_write.txt")
    w_ok, _ = write_text_file(test_file, "Test content line 1\nTest content line 2")
    assert w_ok, "Write file failed"
    r_ok, content = read_text_file(test_file)
    assert r_ok and "line 2" in content, "Read file failed"
    os.remove(test_file)
    print("[OK] Safe read/write file handling verified")


if __name__ == "__main__":
    print("=================================================================")
    print("  RUNNING COMPLETE AUTOMATED TEST SUITE FOR FAKE NEWS ENGINE")
    print("=================================================================")
    test_text_utils()
    test_sorting_utils()
    test_fake_news_detector()
    test_database_manager()
    test_file_handler()
    print("\n=================================================================")
    print("  [SUCCESS] ALL 5 TEST MODULES PASSED! ZERO ERRORS FOUND.")
    print("=================================================================")
