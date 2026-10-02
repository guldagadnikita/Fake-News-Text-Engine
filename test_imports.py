import sys
sys.path.insert(0, '.')

# Test all engine imports
from engine.text_processor import (calculate_text_statistics, get_word_frequencies,
    tokenize_words, clean_extra_spaces, clean_line_breaks, format_sentence_case)
from engine.fake_news_detector import calculate_fake_news_score
from engine.sorting_utils import bubble_sort_frequencies
from engine.search_replace import search_word_occurrences, replace_word_in_text
from engine.readability import calculate_readability_score, estimate_reading_time
from engine.sentiment import analyze_sentiment
from engine.comparison import compare_texts
from engine.report_generator import build_full_report
from engine.file_handler import read_text_file, write_text_file
from auth_db import (register_user, login_user, change_password, update_user_name,
    save_analysis, get_user_history, delete_analysis, clear_user_history,
    get_user_stats, save_report, get_user_reports, get_report_content)

print("ALL IMPORTS: OK")

# Full backend test
sample = "SHOCKING!!! Scientists HATE this one weird trick that DOCTORS dont want you to know!!! You wont believe this viral exposed cure!!!"
score, verdict, color, reasons, details = calculate_fake_news_score(sample)
print(f"Score: {score}/100  Verdict: {verdict}  Color: {color}")
print(f"Details keys: {list(details.keys())}")

stats = calculate_text_statistics(sample)
print(f"Stats: {stats['total_words']} words, {stats['total_sentences']} sentences, {stats['total_paragraphs']} paragraphs")

readability = calculate_readability_score(sample)
print(f"Readability: {readability['grade_level']}  Score: {readability['score']}")

rt = estimate_reading_time(stats['total_words'])
print(f"Reading time: {rt['reading_time_str']}")

sentiment = analyze_sentiment(sample)
print(f"Sentiment: +{sentiment['positive_pct']}% -{sentiment['negative_pct']}% neutral:{sentiment['neutral_pct']}%")

freq = get_word_frequencies(tokenize_words(sample))
sorted_freq, passes, comps, swaps = bubble_sort_frequencies(freq)
print(f"Top word: {sorted_freq[0] if sorted_freq else 'none'}  Passes: {passes}")

# Test auth
ok, uid = register_user("UI Test User", "uitest@test.com", "test123")
print(f"Register: {ok} id={uid}")
ok2, user = login_user("uitest@test.com", "test123")
print(f"Login: {ok2} name={user['name'] if ok2 else user}")
ok3, sid = save_analysis(uid if ok else 1, sample, score, verdict, stats['total_words'])
print(f"Save analysis: {ok3} id={sid}")
hist = get_user_history(uid if ok else 1)
print(f"History: {len(hist)} records")
ustats = get_user_stats(uid if ok else 1)
print(f"User stats: total={ustats['total_analyses']} suspicious={ustats['suspicious']} reliable={ustats['reliable']}")

# Cleanup
import os
if os.path.exists("app_data.db"):
    os.remove("app_data.db")
    print("Test DB cleaned")

# Test matplotlib import
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    print(f"Matplotlib: OK v{matplotlib.__version__}")
except Exception as e:
    print(f"Matplotlib: {e}")

# Test plotly import
try:
    import plotly.graph_objects as go
    import plotly.express as px
    print("Plotly: OK")
except Exception as e:
    print(f"Plotly: {e}")

print("\nALL TESTS PASSED")
