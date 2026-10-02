"""
================================================================================
Module: report_generator.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- String Formatting: f-strings, multi-line templates, alignment specifiers
- Dictionaries: Aggregating results from multiple analysis modules
- Lists: Building formatted line collections for ranked/tabular output
- Functions with Default Arguments: Optional sections gracefully degrade
- Datetime: Timestamping reports
================================================================================
"""

from datetime import datetime


def _bar(pct: float, width: int = 30) -> str:
    """Renders a simple text progress bar for percentage-based metrics."""
    filled = int(round((pct / 100.0) * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def build_full_report(
    title: str,
    text: str,
    stats: dict,
    fake_result: tuple,
    readability: dict,
    sentiment: dict,
    ranked_keywords: list
) -> str:
    """
    Assembles the complete, exportable analysis report as a single string.

    Parameters:
    - title: Display title for the analyzed content
    - text: The raw analyzed text (not included in report for brevity)
    - stats: Output of calculate_text_statistics()
    - fake_result: Tuple (score, verdict, color_hex, reasons_list, details_dict)
    - readability: Output of calculate_readability_score()
    - sentiment: Output of analyze_sentiment()
    - ranked_keywords: List of (word, count) tuples, already sorted descending

    Returns:
    - A formatted multi-section report string, ready to save as .txt
    """
    score, verdict, _color, reasons, details = fake_result
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Calculate lexical density
    lexical_density = 0.0
    if stats.get("total_words", 0) > 0:
        lexical_density = round(
            (stats["unique_words"] / stats["total_words"]) * 100, 1
        )

    # Build reasons block
    reasons_block = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(reasons))

    # Build keyword ranking block
    top_keywords_lines = []
    for rank, (word, count) in enumerate(ranked_keywords[:20], start=1):
        bar_visual = _bar(min(100, int(count) * 5), width=20)
        top_keywords_lines.append(
            f"  {rank:>2}. {word:<20} {count:>4}  {bar_visual}"
        )
    keywords_block = (
        "\n".join(top_keywords_lines) if top_keywords_lines
        else "  No keywords to display."
    )

    # Build repeated words block
    repeated = stats.get("repeated_adjacent_words", [])
    repeated_block = ", ".join(repeated) if repeated else "None detected"

    report = f"""================================================================================
              FAKE NEWS & TEXT ANALYSIS REPORT
================================================================================
Title:            {title if title else 'Untitled Content'}
Generated:        {generated_at}

================================================================================
1. RULE-BASED SUSPICION ANALYSIS
================================================================================
  Suspicion Score:        {score} / 100
  Verdict:                {verdict}
  Risk Level:             {'Low' if score <= 35 else ('Medium' if score <= 65 else 'High')}

  Why This Result:
{reasons_block}

================================================================================
2. TEXT STATISTICS
================================================================================
  Total Words:            {stats.get('total_words', 0)}
  Unique Words:           {stats.get('unique_words', 0)}
  Characters (w/ spaces): {stats.get('characters_with_spaces', 0)}
  Characters (no spaces): {stats.get('characters_without_spaces', 0)}
  Sentences:              {stats.get('total_sentences', 0)}
  Paragraphs:             {stats.get('total_paragraphs', 0)}
  Average Word Length:    {stats.get('average_word_length', 0)}
  Shortest Word:          '{stats.get('shortest_word', 'N/A')}'
  Longest Word:           '{stats.get('longest_word', 'N/A')}'
  Lexical Density:        {lexical_density}%

================================================================================
3. READABILITY ANALYSIS
================================================================================
  Flesch Reading Ease:    {readability.get('score', 'N/A')}  ({readability.get('reading_ease', 'N/A')})
  Grade Level:            {readability.get('grade_level', 'N/A')}
  Interpretation:         {readability.get('interpretation', 'N/A')}
  Avg Words/Sentence:     {readability.get('avg_sentence_length', 'N/A')}
  Avg Syllables/Word:     {readability.get('avg_syllables_per_word', 'N/A')}

================================================================================
4. SENTIMENT / KEYWORD ANALYSIS
================================================================================
  Positive Words:         {sentiment.get('positive_count', 0)}
  Negative Words:         {sentiment.get('negative_count', 0)}
  Result:                 {sentiment.get('result', 'N/A')}
  Positive %:             {sentiment.get('positive_pct', 0)}%  {_bar(sentiment.get('positive_pct', 0), 20)}
  Negative %:             {sentiment.get('negative_pct', 0)}%  {_bar(sentiment.get('negative_pct', 0), 20)}
  Neutral %:              {sentiment.get('neutral_pct', 0)}%  {_bar(sentiment.get('neutral_pct', 0), 20)}

================================================================================
5. REPETITION & REDUNDANCY
================================================================================
  Repeated Adjacent Words: {repeated_block}
  ALL-CAPS Words:          {stats.get('uppercase_words_count', 0)}

================================================================================
6. KEYWORD FREQUENCY RANKING (Top 20)
================================================================================
{keywords_block}

================================================================================
DISCLAIMER
================================================================================
  This report was generated by the Fake News & Text Processing Engine.
  Rule-based analysis only. This tool identifies suspicious writing
  patterns and does NOT verify factual accuracy.
================================================================================
"""
    return report
