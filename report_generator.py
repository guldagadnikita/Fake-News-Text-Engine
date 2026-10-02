"""
================================================================================
Module: report_generator.py
================================================================================
Python Concepts Demonstrated:
- String Formatting: f-strings, multi-line templates, alignment specifiers
- Dictionaries: Aggregating results from multiple analysis modules
- Lists: Building formatted line collections for ranked/tabular output
- Functions with Default Arguments: Optional sections gracefully degrade
================================================================================
Builds the single consolidated ".txt" report used by the
"Export & Report Generator" feature. Pulls together every analysis module's
output (credibility, readability, sentiment, volume stats, keyword ranking)
into one clean, presentation-ready document.
================================================================================
"""

from datetime import datetime


def _bar(pct: float, width: int = 30) -> str:
    """Renders a simple text progress bar for percentage-based metrics."""
    filled = int(round((pct / 100.0) * width))
    filled = max(0, min(width, filled))
    return "#" * filled + "-" * (width - filled)


def build_full_report(
    title: str,
    text: str,
    stats: dict,
    fake_result: tuple,
    readability: dict,
    reading_time: dict,
    sentiment: dict,
    ranked_keywords: list
) -> str:
    """
    Assembles the complete, exportable analysis report as a single string.

    Parameters:
    - title: Display title for the analyzed content
    - text: The raw analyzed text
    - stats: Output of calculate_text_statistics()
    - fake_result: Tuple (score, verdict, color_hex, reasons_list, details_dict)
    - readability: Output of calculate_readability_score()
    - reading_time: Output of estimate_reading_time()
    - sentiment: Output of analyze_tone_sentiment()
    - ranked_keywords: List of (word, count) tuples, already sorted descending

    Returns:
    - A formatted multi-section report string, ready to save as .txt
    """
    score, verdict, _color, reasons, details = fake_result
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lexical_density = 0.0
    if stats.get("total_words", 0) > 0:
        lexical_density = round((stats["unique_words"] / stats["total_words"]) * 100, 1)

    reasons_block = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(reasons))

    top_keywords_lines = []
    for rank, (word, count) in enumerate(ranked_keywords[:20], start=1):
        top_keywords_lines.append(f"  {rank:>2}. {word:<20} {count:>4}  {_bar(min(100, count * 5))}")
    keywords_block = "\n".join(top_keywords_lines) if top_keywords_lines else "  No keywords to display."

    repeated = stats.get("repeated_adjacent_words", [])
    repeated_block = ", ".join(repeated) if repeated else "None detected"

    report = f"""================================================================================
                    CONTENT ANALYSIS & CREDIBILITY REPORT
================================================================================
Title:            {title if title else 'Untitled Content'}
Generated:        {generated_at}

--------------------------------------------------------------------------------
1. CREDIBILITY & RISK ASSESSMENT
--------------------------------------------------------------------------------
  Authenticity Score:     {score} / 100
  Verdict:                {verdict}
  Risk Level:             {'Low Risk' if score <= 35 else ('Moderate Caution' if score <= 65 else 'High Suspicion')}

  Risk Factor Breakdown:
{reasons_block}

--------------------------------------------------------------------------------
2. READABILITY & COMPREHENSION INDEX
--------------------------------------------------------------------------------
  Flesch Reading Ease:    {readability.get('score', 'N/A')}  ({readability.get('reading_ease', 'N/A')})
  Estimated Grade Level:  {readability.get('grade_level', 'N/A')}
  Interpretation:         {readability.get('interpretation', 'N/A')}
  Avg Sentence Length:    {readability.get('avg_sentence_length', 'N/A')} words
  Avg Syllables/Word:     {readability.get('avg_syllables_per_word', 'N/A')}

--------------------------------------------------------------------------------
3. READING TIME & SPEAKING DURATION
--------------------------------------------------------------------------------
  Silent Reading Time:    {reading_time.get('reading_time_str', 'N/A')}  (~200 wpm)
  Speaking Duration:      {reading_time.get('speaking_time_str', 'N/A')}  (~130 wpm)

--------------------------------------------------------------------------------
4. TONE & SENTIMENT DISTRIBUTION
--------------------------------------------------------------------------------
  Positive:      {sentiment.get('positive_pct', 0):>5}%   {_bar(sentiment.get('positive_pct', 0))}
  Neutral:       {sentiment.get('neutral_pct', 0):>5}%   {_bar(sentiment.get('neutral_pct', 0))}
  Negative:      {sentiment.get('negative_pct', 0):>5}%   {_bar(sentiment.get('negative_pct', 0))}
  Sensational:   {sentiment.get('sensational_pct', 0):>5}%   {_bar(sentiment.get('sensational_pct', 0))}
  Predominant Tone:       {sentiment.get('predominant_tone', 'N/A')}

--------------------------------------------------------------------------------
5. CORE VOLUME ANALYTICS
--------------------------------------------------------------------------------
  Total Words:            {stats.get('total_words', 0)}
  Unique Words:           {stats.get('unique_words', 0)}
  Characters (w/ spaces): {stats.get('characters_with_spaces', 0)}
  Characters (no spaces): {stats.get('characters_without_spaces', 0)}
  Sentences:              {stats.get('total_sentences', 0)}
  Paragraphs:             {stats.get('total_paragraphs', 0)}

--------------------------------------------------------------------------------
6. LEXICAL DENSITY & WORD LENGTHS
--------------------------------------------------------------------------------
  Lexical Density:        {lexical_density}%  (unique words / total words)
  Average Word Length:    {stats.get('average_word_length', 0)} characters
  Shortest Word:          '{stats.get('shortest_word', 'N/A')}'
  Longest Word:           '{stats.get('longest_word', 'N/A')}'

--------------------------------------------------------------------------------
7. REPETITION & REDUNDANCY INSPECTOR
--------------------------------------------------------------------------------
  Repeated Adjacent Words: {repeated_block}
  ALL-CAPS Words:          {stats.get('uppercase_words_count', 0)}

--------------------------------------------------------------------------------
8. KEYWORD FREQUENCY RANKING (Top 20)
--------------------------------------------------------------------------------
{keywords_block}

================================================================================
Report generated by the Content Analysis & Credibility Engine.
This is a rule-based heuristic tool and does not perform live fact-checking.
================================================================================
"""
    return report
