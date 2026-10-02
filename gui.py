"""
================================================================================
Module: gui.py
================================================================================
Python & Tkinter Concepts Demonstrated:
- Object-Oriented Programming (OOP): FakeNewsApp encapsulates all UI logic
- Tkinter Layout Management: Frame, Label, Button, Entry, Text, Canvas+Scrollbar
- Multi-Page Dashboard Pattern: stacked frames raised via tkraise()
- Tkinter Advanced Widgets: ttk.Treeview (Data Table), ttk.Combobox, ttk.Progressbar
- Event Handling & Callbacks: Button commands, keyboard shortcuts, Treeview selection
- Modal Dialogs: Toplevel windows for Search & Replace and Database Settings
- Standard Dialogs: messagebox, filedialog
- Integration: Coordinates utils.text_utils, utils.sorting_utils, fake_news_detector,
  file_handler, database, and report_generator modules
================================================================================
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from utils.text_utils import (
    calculate_text_statistics,
    get_word_frequencies,
    tokenize_words,
    clean_extra_spaces,
    clean_line_breaks,
    format_sentence_case,
    search_word_occurrences,
    replace_word_in_text,
    calculate_readability_score,
    estimate_reading_time,
    analyze_tone_sentiment,
)
from utils.sorting_utils import bubble_sort_frequencies
from fake_news_detector import calculate_fake_news_score
from file_handler import read_text_file, write_text_file, load_keywords_from_file
from database import DatabaseManager
from report_generator import build_full_report


class FakeNewsApp:
    """Main Application GUI Class — a full-width, page-based analysis dashboard."""

    NAV_ITEMS = [
        ("credibility", "🛡️  Credibility & Risk Assessment"),
        ("analytics", "📊  Content Analytics & Readability"),
        ("keywords", "🔑  Keyword Insights & Trends"),
        ("archives", "🗄️  Saved Archives"),
    ]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Content Analysis & Credibility Engine")
        self.root.geometry("1200x820")
        self.root.minsize(1100, 720)

        # ---- Color Palette - Modern Slate Dashboard ----
        self.COLOR_BG = "#F1F5F9"
        self.COLOR_HEADER = "#0F172A"
        self.COLOR_CARD = "#FFFFFF"
        self.COLOR_BORDER = "#E2E8F0"
        self.COLOR_PRIMARY = "#2563EB"
        self.COLOR_PRIMARY_DARK = "#1D4ED8"
        self.COLOR_SUCCESS = "#16A34A"
        self.COLOR_WARNING = "#D97706"
        self.COLOR_DANGER = "#DC2626"
        self.COLOR_TEXT_MAIN = "#1E293B"
        self.COLOR_TEXT_MUTED = "#64748B"
        self.COLOR_NAV_ACTIVE = "#1D4ED8"
        self.COLOR_NAV_INACTIVE = "#334155"

        self.root.configure(bg=self.COLOR_BG)

        # ---- Backend State ----
        self.db = DatabaseManager(host="localhost", user="root", password="root", database="fake_news_db")
        self.db_connected = False
        self.keywords_dict = {"suspicious": [], "clickbait": [], "credible": []}
        self.last_analysis = None
        self.last_ranked_keywords = []

        # Widget reference dictionaries populated during page construction
        self.nav_buttons = {}
        self.pages = {}
        self.active_page = "credibility"

        # ---- Build UI ----
        self._setup_styles()
        self._build_header()
        self._build_input_card()
        self._build_nav_bar()
        self._build_page_container()
        self._build_status_bar()

        self.show_page("credibility")
        self._init_backend_resources()

    # =========================================================================
    # STYLES
    # =========================================================================
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.COLOR_TEXT_MAIN,
            font=("Segoe UI", 9),
            rowheight=28,
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#E2E8F0",
            foreground=self.COLOR_TEXT_MAIN,
        )
        style.map("Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", "#1E3A8A")])

        style.configure("Positive.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.COLOR_SUCCESS)
        style.configure("Negative.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.COLOR_DANGER)
        style.configure("Neutral.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.COLOR_TEXT_MUTED)
        style.configure("Sensational.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.COLOR_WARNING)
        style.configure("Keyword.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.COLOR_PRIMARY)
        style.configure("Score.Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.COLOR_PRIMARY)

    # =========================================================================
    # SHELL: HEADER / INPUT CARD / NAV BAR / STATUS BAR
    # =========================================================================
    def _build_header(self):
        header = tk.Frame(self.root, bg=self.COLOR_HEADER, padx=24, pady=14)
        header.pack(fill=tk.X, side=tk.TOP)

        title_box = tk.Frame(header, bg=self.COLOR_HEADER)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box, text="Content Analysis & Credibility Engine",
            font=("Segoe UI", 16, "bold"), fg="#FFFFFF", bg=self.COLOR_HEADER
        ).pack(anchor="w")

        tk.Label(
            title_box, text="Readability • Sentiment • Credibility Scoring • Keyword Intelligence",
            font=("Segoe UI", 9), fg="#94A3B8", bg=self.COLOR_HEADER
        ).pack(anchor="w")

        status_box = tk.Frame(header, bg=self.COLOR_HEADER)
        status_box.pack(side=tk.RIGHT, pady=4)

        self.db_status_badge = tk.Label(
            status_box, text="🟡 Connecting…", font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF", bg="#475569", padx=10, pady=4, relief=tk.FLAT
        )
        self.db_status_badge.pack(side=tk.LEFT, padx=6)

        tk.Button(
            status_box, text="⚙️ Settings", font=("Segoe UI", 8, "bold"),
            bg="#334155", fg="#FFFFFF", activebackground="#475569", activeforeground="#FFFFFF",
            relief=tk.FLAT, padx=8, pady=3, cursor="hand2", command=self._open_db_settings_dialog
        ).pack(side=tk.LEFT)

    def _build_input_card(self):
        outer = tk.Frame(self.root, bg=self.COLOR_BG, padx=24)
        outer.pack(fill=tk.X, side=tk.TOP, pady=(16, 8))

        card = tk.Frame(outer, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER,
                         highlightthickness=1, padx=16, pady=12)
        card.pack(fill=tk.X)

        top_bar = tk.Frame(card, bg=self.COLOR_CARD)
        top_bar.pack(fill=tk.X, pady=(0, 6))

        tk.Label(top_bar, text="📝 Content Input", font=("Segoe UI", 11, "bold"),
                 fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD).pack(side=tk.LEFT)

        sample_frame = tk.Frame(top_bar, bg=self.COLOR_CARD)
        sample_frame.pack(side=tk.RIGHT)
        tk.Button(sample_frame, text="Load Reliable Sample", font=("Segoe UI", 8), bg="#EFF6FF",
                  fg=self.COLOR_PRIMARY, relief=tk.GROOVE, padx=6, pady=2, cursor="hand2",
                  command=lambda: self._load_preset_sample("reliable")).pack(side=tk.LEFT, padx=2)
        tk.Button(sample_frame, text="Load Clickbait Sample", font=("Segoe UI", 8), bg="#FEF2F2",
                  fg=self.COLOR_DANGER, relief=tk.GROOVE, padx=6, pady=2, cursor="hand2",
                  command=lambda: self._load_preset_sample("suspicious")).pack(side=tk.LEFT, padx=2)

        text_frame = tk.Frame(card, bg=self.COLOR_CARD)
        text_frame.pack(fill=tk.X)

        self.text_editor = tk.Text(
            text_frame, wrap=tk.WORD, font=("Consolas", 10), height=6,
            bg="#FAFAFA", fg="#0F172A", insertbackground="#0F172A", padx=8, pady=8,
            relief=tk.FLAT, highlightbackground=self.COLOR_BORDER, highlightthickness=1
        )
        editor_scroll = tk.Scrollbar(text_frame, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=editor_scroll.set)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.tag_configure("search_highlight", background="#FEF08A", foreground="#000000")
        self.text_editor.bind("<KeyRelease>", self._update_live_counts)

        self.editor_count_lbl = tk.Label(
            card, text="Words: 0 | Characters: 0", font=("Segoe UI", 8),
            fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD, anchor="e"
        )
        self.editor_count_lbl.pack(fill=tk.X, pady=(4, 6))

        # Primary actions
        action_bar = tk.Frame(card, bg=self.COLOR_CARD)
        action_bar.pack(fill=tk.X, pady=(0, 4))

        self._make_button(action_bar, "🚀 Analyze Content", self.COLOR_PRIMARY, self.run_full_analysis,
                           bold=True).pack(side=tk.LEFT, padx=(0, 4))
        self._make_button(action_bar, "🛡️ Credibility Check", self.COLOR_DANGER, self.run_fake_news_only,
                           bold=True).pack(side=tk.LEFT, padx=4)
        self._make_button(action_bar, "💾 Save to Archive", self.COLOR_SUCCESS,
                           self.save_current_analysis_to_db, bold=True).pack(side=tk.LEFT, padx=4)
        self._make_button(action_bar, "📄 Export Report", "#7C3AED", self.export_full_report,
                           bold=True).pack(side=tk.LEFT, padx=4)
        self._make_button(action_bar, "🧹 Clear", "#E2E8F0", self.clear_all,
                           fg=self.COLOR_TEXT_MAIN).pack(side=tk.LEFT, padx=4)

        # Secondary tools
        tools_bar = tk.Frame(card, bg=self.COLOR_CARD)
        tools_bar.pack(fill=tk.X)

        tools = [
            ("🔍 Search", self._open_search_dialog),
            ("✏️ Batch Replace", self._open_replace_dialog),
            ("✨ Normalize Spacing", self._clean_spaces_action),
            ("📐 Clean Line Breaks", self._clean_lines_action),
            ("UPPER", lambda: self._convert_case_action("upper")),
            ("lower", lambda: self._convert_case_action("lower")),
            ("Title", lambda: self._convert_case_action("title")),
            ("Sentence.", lambda: self._convert_case_action("sentence")),
            ("📂 Open File", self.open_text_file_dialog),
            ("💾 Save Text", self.save_text_file_dialog),
        ]
        for label, cmd in tools:
            tk.Button(
                tools_bar, text=label, font=("Segoe UI", 8), bg="#F1F5F9", fg=self.COLOR_TEXT_MAIN,
                relief=tk.GROOVE, padx=6, pady=3, cursor="hand2", command=cmd
            ).pack(side=tk.LEFT, padx=2, pady=(2, 0))

    def _make_button(self, parent, text, bg, command, fg="#FFFFFF", bold=False):
        return tk.Button(
            parent, text=text, font=("Segoe UI", 9, "bold" if bold else "normal"), bg=bg, fg=fg,
            activebackground=bg, activeforeground=fg, relief=tk.FLAT, padx=12, pady=6,
            cursor="hand2", command=command
        )

    def _build_nav_bar(self):
        nav_outer = tk.Frame(self.root, bg=self.COLOR_BG, padx=24)
        nav_outer.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))

        nav_bar = tk.Frame(nav_outer, bg=self.COLOR_HEADER)
        nav_bar.pack(fill=tk.X)

        for key, label in self.NAV_ITEMS:
            btn = tk.Button(
                nav_bar, text=label, font=("Segoe UI", 9, "bold"),
                bg=self.COLOR_NAV_INACTIVE, fg="#CBD5E1",
                activebackground=self.COLOR_NAV_ACTIVE, activeforeground="#FFFFFF",
                relief=tk.FLAT, padx=16, pady=10, cursor="hand2",
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.nav_buttons[key] = btn

    def _build_page_container(self):
        container = tk.Frame(self.root, bg=self.COLOR_BG, padx=24)
        container.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages["credibility"] = self._build_scrollable_page(container)
        self._build_page_credibility(self.pages["credibility"])

        self.pages["analytics"] = self._build_scrollable_page(container)
        self._build_page_analytics(self.pages["analytics"])

        self.pages["keywords"] = self._build_scrollable_page(container)
        self._build_page_keywords(self.pages["keywords"])

        self.pages["archives"] = self._build_scrollable_page(container)
        self._build_page_archives(self.pages["archives"])

    def _build_scrollable_page(self, container) -> tk.Frame:
        """Wraps page content in a canvas so full-width card stacks can scroll vertically."""
        outer = tk.Frame(container, bg=self.COLOR_BG)
        outer.grid(row=0, column=0, sticky="nsew")

        canvas = tk.Canvas(outer, bg=self.COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        inner = tk.Frame(canvas, bg=self.COLOR_BG)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", on_configure)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # inner.master trick lets us later reach `outer` from `inner` for grid placement
        inner.master_outer = outer
        return inner

    def show_page(self, key: str):
        """Raises the requested page and updates nav button active styling."""
        self.pages[key].master_outer.tkraise()
        self.active_page = key
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg=self.COLOR_NAV_ACTIVE, fg="#FFFFFF")
            else:
                btn.config(bg=self.COLOR_NAV_INACTIVE, fg="#CBD5E1")

    def _build_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#E2E8F0", padx=24, pady=4)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = tk.Label(status_frame, text="Ready • Content Analysis & Credibility Engine",
                                    font=("Segoe UI", 8), fg=self.COLOR_TEXT_MAIN, bg="#E2E8F0")
        self.status_lbl.pack(side=tk.LEFT)

        tk.Label(status_frame, text="⚠️ Rule-Based Heuristic Analysis (Not a live fact-checker)",
                 font=("Segoe UI", 8, "italic"), fg=self.COLOR_TEXT_MUTED, bg="#E2E8F0").pack(side=tk.RIGHT)

    # =========================================================================
    # CARD HELPER
    # =========================================================================
    def _card(self, parent, title=None) -> tk.Frame:
        """Creates a full-width modern card container with generous margins."""
        card = tk.Frame(parent, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER,
                         highlightthickness=1, padx=20, pady=16)
        card.pack(fill=tk.X, padx=4, pady=(0, 16), anchor="n")
        if title:
            tk.Label(card, text=title, font=("Segoe UI", 12, "bold"),
                     fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 10))
        return card

    # =========================================================================
    # PAGE 1: CREDIBILITY & RISK ASSESSMENT
    # =========================================================================
    def _build_page_credibility(self, parent):
        tk.Frame(parent, height=8, bg=self.COLOR_BG).pack()

        score_card = self._card(parent)
        top_row = tk.Frame(score_card, bg=self.COLOR_CARD)
        top_row.pack(fill=tk.X)

        left = tk.Frame(top_row, bg=self.COLOR_CARD)
        left.pack(side=tk.LEFT, anchor="w")
        self.lbl_score_number = tk.Label(left, text="Score: -- / 100", font=("Segoe UI", 26, "bold"),
                                          fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD)
        self.lbl_score_number.pack(anchor="w")
        self.lbl_verdict_summary = tk.Label(
            left, text="Paste content above and click 'Analyze Content' to begin.",
            font=("Segoe UI", 9, "italic"), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD,
            wraplength=700, justify=tk.LEFT
        )
        self.lbl_verdict_summary.pack(anchor="w", pady=(4, 0))

        right = tk.Frame(top_row, bg=self.COLOR_CARD)
        right.pack(side=tk.RIGHT, anchor="e")
        self.verdict_badge = tk.Label(right, text="READY TO ANALYZE", font=("Segoe UI", 12, "bold"),
                                       bg="#E2E8F0", fg=self.COLOR_TEXT_MAIN, padx=18, pady=10, relief=tk.FLAT)
        self.verdict_badge.pack()

        self.score_progress = ttk.Progressbar(score_card, style="Score.Horizontal.TProgressbar",
                                               orient="horizontal", mode="determinate", maximum=100, value=0)
        self.score_progress.pack(fill=tk.X, pady=(14, 0))

        risk_card = self._card(parent, "Risk Factor Breakdown")
        self.txt_fake_output = self._create_scrollable_text(risk_card, height=14)

    # =========================================================================
    # PAGE 2: CONTENT ANALYTICS & READABILITY
    # =========================================================================
    def _build_page_analytics(self, parent):
        tk.Frame(parent, height=8, bg=self.COLOR_BG).pack()

        # --- Core Volume Analytics ---
        volume_card = self._card(parent, "Core Volume Analytics")
        volume_row = tk.Frame(volume_card, bg=self.COLOR_CARD)
        volume_row.pack(fill=tk.X)
        self.card_values = {}
        metrics = [
            ("TOTAL WORDS", "0", "#3B82F6"), ("UNIQUE WORDS", "0", "#8B5CF6"),
            ("SENTENCES", "0", "#10B981"), ("PARAGRAPHS", "0", "#F59E0B"),
            ("CHARACTERS", "0", "#EC4899"), ("AVG WORD LEN", "0.0", "#0EA5E9"),
        ]
        for title, default_val, accent in metrics:
            cell = tk.Frame(volume_row, bg="#F8FAFC", highlightbackground=self.COLOR_BORDER,
                             highlightthickness=1, padx=10, pady=8)
            cell.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)
            tk.Label(cell, text=title, font=("Segoe UI", 8, "bold"), fg=self.COLOR_TEXT_MUTED,
                     bg="#F8FAFC").pack(anchor="w")
            val_lbl = tk.Label(cell, text=default_val, font=("Segoe UI", 16, "bold"), fg=accent, bg="#F8FAFC")
            val_lbl.pack(anchor="w", pady=(2, 0))
            self.card_values[title] = val_lbl

        # --- Readability + Reading Time side by side ---
        rr_outer = tk.Frame(parent, bg=self.COLOR_BG)
        rr_outer.pack(fill=tk.X, padx=4, pady=(0, 16))

        read_card = tk.Frame(rr_outer, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER,
                              highlightthickness=1, padx=20, pady=16)
        read_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        tk.Label(read_card, text="Readability & Comprehension Index", font=("Segoe UI", 12, "bold"),
                 fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 8))
        self.lbl_flesch_score = tk.Label(read_card, text="-- / 100", font=("Segoe UI", 22, "bold"),
                                          fg=self.COLOR_PRIMARY, bg=self.COLOR_CARD)
        self.lbl_flesch_score.pack(anchor="w")
        self.lbl_flesch_ease = tk.Label(read_card, text="Reading Ease: --", font=("Segoe UI", 9, "bold"),
                                         fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD)
        self.lbl_flesch_ease.pack(anchor="w", pady=(6, 0))
        self.lbl_flesch_grade = tk.Label(read_card, text="Grade Level: --", font=("Segoe UI", 9),
                                          fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD)
        self.lbl_flesch_grade.pack(anchor="w")
        self.lbl_flesch_interp = tk.Label(read_card, text="Analyze content to see readability results.",
                                           font=("Segoe UI", 8, "italic"), fg=self.COLOR_TEXT_MUTED,
                                           bg=self.COLOR_CARD, wraplength=380, justify=tk.LEFT)
        self.lbl_flesch_interp.pack(anchor="w", pady=(6, 0))

        time_card = tk.Frame(rr_outer, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER,
                              highlightthickness=1, padx=20, pady=16)
        time_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        tk.Label(time_card, text="Reading Time & Speaking Duration", font=("Segoe UI", 12, "bold"),
                 fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 8))
        tk.Label(time_card, text="📖 Silent Reading (200 wpm)", font=("Segoe UI", 9, "bold"),
                 fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD).pack(anchor="w")
        self.lbl_reading_time = tk.Label(time_card, text="--", font=("Segoe UI", 18, "bold"),
                                          fg=self.COLOR_SUCCESS, bg=self.COLOR_CARD)
        self.lbl_reading_time.pack(anchor="w", pady=(0, 10))
        tk.Label(time_card, text="🎙️ Speaking Duration (130 wpm)", font=("Segoe UI", 9, "bold"),
                 fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD).pack(anchor="w")
        self.lbl_speaking_time = tk.Label(time_card, text="--", font=("Segoe UI", 18, "bold"),
                                           fg=self.COLOR_WARNING, bg=self.COLOR_CARD)
        self.lbl_speaking_time.pack(anchor="w")

        # --- Tone & Sentiment Distribution ---
        sentiment_card = self._card(parent, "Tone & Sentiment Distribution")
        self.sentiment_bars = {}
        sentiment_rows = [
            ("Positive", "Positive.Horizontal.TProgressbar", self.COLOR_SUCCESS),
            ("Neutral", "Neutral.Horizontal.TProgressbar", self.COLOR_TEXT_MUTED),
            ("Negative", "Negative.Horizontal.TProgressbar", self.COLOR_DANGER),
            ("Sensational", "Sensational.Horizontal.TProgressbar", self.COLOR_WARNING),
        ]
        for label, style_name, color in sentiment_rows:
            row = tk.Frame(sentiment_card, bg=self.COLOR_CARD)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 9, "bold"), fg=color, bg=self.COLOR_CARD,
                     width=13, anchor="w").pack(side=tk.LEFT)
            bar = ttk.Progressbar(row, style=style_name, orient="horizontal", mode="determinate",
                                   maximum=100, value=0)
            bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
            pct_lbl = tk.Label(row, text="0.0%", font=("Segoe UI", 9), fg=self.COLOR_TEXT_MAIN,
                                bg=self.COLOR_CARD, width=6, anchor="e")
            pct_lbl.pack(side=tk.LEFT)
            self.sentiment_bars[label] = (bar, pct_lbl)
        self.lbl_predominant_tone = tk.Label(sentiment_card, text="Predominant Tone: --",
                                              font=("Segoe UI", 9, "italic"), fg=self.COLOR_TEXT_MUTED,
                                              bg=self.COLOR_CARD)
        self.lbl_predominant_tone.pack(anchor="w", pady=(8, 0))

        # --- Lexical Density + Repetition side by side ---
        lr_outer = tk.Frame(parent, bg=self.COLOR_BG)
        lr_outer.pack(fill=tk.X, padx=4, pady=(0, 16))

        lex_card = tk.Frame(lr_outer, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER,
                             highlightthickness=1, padx=20, pady=16)
        lex_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        tk.Label(lex_card, text="Lexical Density & Word Lengths", font=("Segoe UI", 12, "bold"),
                 fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 8))
        self.lbl_lexical_density = tk.Label(lex_card, text="Lexical Density: --%", font=("Segoe UI", 11, "bold"),
                                             fg=self.COLOR_PRIMARY, bg=self.COLOR_CARD)
        self.lbl_lexical_density.pack(anchor="w")
        self.lbl_word_lengths = tk.Label(lex_card, text="Shortest: -- | Longest: --", font=("Segoe UI", 9),
                                          fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD)
        self.lbl_word_lengths.pack(anchor="w", pady=(4, 0))

        rep_card = tk.Frame(lr_outer, bg=self.COLOR_CARD, highlightbackground=self.COLOR_BORDER,
                             highlightthickness=1, padx=20, pady=16)
        rep_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        tk.Label(rep_card, text="Repetition & Redundancy Inspector", font=("Segoe UI", 12, "bold"),
                 fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_CARD).pack(anchor="w", pady=(0, 8))
        self.lbl_repetition = tk.Label(rep_card, text="No content analyzed yet.", font=("Segoe UI", 9),
                                        fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD, wraplength=380,
                                        justify=tk.LEFT)
        self.lbl_repetition.pack(anchor="w")

    # =========================================================================
    # PAGE 3: KEYWORD INSIGHTS & TRENDS
    # =========================================================================
    def _build_page_keywords(self, parent):
        tk.Frame(parent, height=8, bg=self.COLOR_BG).pack()
        card = self._card(parent, "Keyword Frequency Ranking")

        tk.Label(card, text="Ranked by occurrence count across the analyzed content.",
                 font=("Segoe UI", 8, "italic"), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD).pack(anchor="w",
                                                                                                       pady=(0, 8))

        self.keyword_rows_frame = tk.Frame(card, bg=self.COLOR_CARD)
        self.keyword_rows_frame.pack(fill=tk.X)
        self.lbl_keywords_empty = tk.Label(self.keyword_rows_frame, text="Analyze content to see ranked keywords.",
                                            font=("Segoe UI", 9, "italic"), fg=self.COLOR_TEXT_MUTED,
                                            bg=self.COLOR_CARD)
        self.lbl_keywords_empty.pack(anchor="w", pady=8)

    # =========================================================================
    # PAGE 4: SAVED ARCHIVES
    # =========================================================================
    def _build_page_archives(self, parent):
        tk.Frame(parent, height=8, bg=self.COLOR_BG).pack()
        card = self._card(parent, "Saved Archives")

        controls = tk.Frame(card, bg=self.COLOR_CARD)
        controls.pack(fill=tk.X, pady=(0, 10))

        tk.Label(controls, text="Filter Verdict:", font=("Segoe UI", 9, "bold"),
                 bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MAIN).pack(side=tk.LEFT, padx=(0, 4))

        self.filter_combobox = ttk.Combobox(
            controls, values=["All", "Likely Reliable", "Possibly Misleading", "Suspicious / Likely Fake"],
            state="readonly", width=24
        )
        self.filter_combobox.set("All")
        self.filter_combobox.pack(side=tk.LEFT, padx=4)
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_database_history())

        tk.Button(controls, text="🔄 Refresh", font=("Segoe UI", 8), bg="#E2E8F0", relief=tk.GROOVE,
                  padx=6, pady=2, cursor="hand2", command=self.load_database_history).pack(side=tk.LEFT, padx=4)

        tk.Button(controls, text="📥 Load to Editor", font=("Segoe UI", 8, "bold"), bg="#DBEAFE",
                  fg=self.COLOR_PRIMARY, relief=tk.GROOVE, padx=8, pady=2, cursor="hand2",
                  command=self._load_selected_history_record).pack(side=tk.RIGHT, padx=4)

        tk.Button(controls, text="🗑️ Delete", font=("Segoe UI", 8), bg="#FEE2E2", fg=self.COLOR_DANGER,
                  relief=tk.GROOVE, padx=8, pady=2, cursor="hand2",
                  command=self._delete_selected_history_record).pack(side=tk.RIGHT, padx=2)

        tree_frame = tk.Frame(card, bg=self.COLOR_CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "created_at", "title", "words", "score", "verdict")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse", height=14)
        headings = {"id": "ID", "created_at": "Date & Time", "title": "Title / Snippet",
                    "words": "Words", "score": "Score", "verdict": "Verdict"}
        widths = {"id": 50, "created_at": 140, "title": 320, "words": 70, "score": 70, "verdict": 170}
        anchors = {"id": "center", "created_at": "center", "title": "w", "words": "center",
                   "score": "center", "verdict": "w"}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=anchors[col])

        tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", lambda e: self._load_selected_history_record())

    def _create_scrollable_text(self, parent, height=12) -> tk.Text:
        box_frame = tk.Frame(parent, bg=self.COLOR_CARD)
        box_frame.pack(fill=tk.BOTH, expand=True)
        txt = tk.Text(box_frame, wrap=tk.WORD, font=("Consolas", 9), height=height,
                       bg="#FAFAFA", fg="#0F172A", padx=10, pady=10, relief=tk.FLAT,
                       highlightbackground=self.COLOR_BORDER, highlightthickness=1, state=tk.DISABLED)
        scroll = tk.Scrollbar(box_frame, command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return txt

    # =========================================================================
    # BACKEND INITIALIZATION & DATABASE
    # =========================================================================
    def _init_backend_resources(self):
        kw_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "keywords.txt")
        if os.path.exists(kw_path):
            success, result = load_keywords_from_file(kw_path)
            if success:
                self.keywords_dict = result
            else:
                self.status_lbl.config(text=f"Notice: Using default fallback keywords ({result})")
        else:
            self.status_lbl.config(text="Notice: keywords.txt not found, using default keyword banks.")
        self._connect_mysql_database()

    def _connect_mysql_database(self):
        try:
            test_success, _test_msg = self.db.test_connection()
            if test_success:
                init_success, _init_msg = self.db.initialize_database()
                if init_success:
                    self.db_connected = True
                    self.db_status_badge.config(text="🟢 Database Connected", bg=self.COLOR_SUCCESS)
                    self.db.seed_keywords_into_db(self.keywords_dict)
                    self.load_database_history()
                else:
                    self.db_status_badge.config(text="🔴 DB Init Failed", bg=self.COLOR_DANGER)
            else:
                self.db_connected = False
                self.db_status_badge.config(text="🔴 Database Disconnected", bg=self.COLOR_DANGER)
        except Exception:
            self.db_connected = False
            self.db_status_badge.config(text="🔴 Database Offline", bg=self.COLOR_DANGER)

    # =========================================================================
    # CORE ACTIONS: ANALYSIS
    # =========================================================================
    def get_input_text(self) -> str:
        return self.text_editor.get("1.0", tk.END).strip()

    def run_full_analysis(self):
        text = self.get_input_text()
        if not text:
            messagebox.showwarning("Empty Input", "Please enter or paste content before analyzing.")
            return

        stats = calculate_text_statistics(text)
        fake_result = calculate_fake_news_score(text, self.keywords_dict)
        readability = calculate_readability_score(text)
        reading_time = estimate_reading_time(stats["total_words"])
        sentiment = analyze_tone_sentiment(text)

        words_list = tokenize_words(text, keep_case=False)
        freq_dict = get_word_frequencies(words_list)
        sorted_freqs, _passes, _comparisons, _swaps = bubble_sort_frequencies(list(freq_dict.items()),
                                                                               descending=True)
        self.last_ranked_keywords = sorted_freqs

        self._refresh_credibility_page(fake_result, stats)
        self._refresh_analytics_page(stats, readability, reading_time, sentiment)
        self._refresh_keywords_page(sorted_freqs)

        score, verdict, _color, reasons, _details = fake_result
        self.last_analysis = {
            "title": text.split("\n")[0][:60].strip(),
            "full_text": text,
            "stats": stats,
            "score": score,
            "verdict": verdict,
            "reasons": reasons,
            "readability": readability,
            "reading_time": reading_time,
            "sentiment": sentiment,
        }

        self.status_lbl.config(
            text=f"Analysis complete • {stats['total_words']} words • Score {score}/100 ({verdict})"
        )

    def run_fake_news_only(self):
        self.run_full_analysis()
        self.show_page("credibility")

    # ---- Page refreshers ----
    def _refresh_credibility_page(self, fake_result, stats):
        score, verdict, color, reasons, details = fake_result

        self.verdict_badge.config(text=verdict.upper(), bg=color, fg="#FFFFFF")
        self.lbl_score_number.config(text=f"Score: {score} / 100", fg=color)
        self.lbl_verdict_summary.config(
            text=f"Analysis completed across {stats['total_words']} words and {stats['total_sentences']} sentences."
        )
        self.score_progress.configure(value=score)

        reasons_formatted = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(reasons))
        report = f"""RISK LEVEL: {'LOW RISK' if score <= 35 else ('MODERATE CAUTION' if score <= 65 else 'HIGH SUSPICION')}

--------------------------------------------------------------------------------
DETECTED SIGNALS
--------------------------------------------------------------------------------
{reasons_formatted}

--------------------------------------------------------------------------------
TECHNICAL SUMMARY
--------------------------------------------------------------------------------
  Sensational Language:    {len(details.get('suspicious_matches', []))} indicator(s)
  Clickbait Structure:     {len(details.get('clickbait_matches', []))} phrase(s)
  Attribution Signals:     {len(details.get('credible_matches', []))} source(s)
  ALL-CAPS Ratio:          {details.get('caps_ratio', 0.0)}%
  Emotional Punctuation:   {details.get('punct_clusters', 0)} cluster(s)

This is a rule-based heuristic tool and does not perform live fact-checking.
"""
        self.txt_fake_output.config(state=tk.NORMAL)
        self.txt_fake_output.delete("1.0", tk.END)
        self.txt_fake_output.insert(tk.END, report)
        self.txt_fake_output.config(state=tk.DISABLED)

    def _refresh_analytics_page(self, stats, readability, reading_time, sentiment):
        self.card_values["TOTAL WORDS"].config(text=str(stats["total_words"]))
        self.card_values["UNIQUE WORDS"].config(text=str(stats["unique_words"]))
        self.card_values["SENTENCES"].config(text=str(stats["total_sentences"]))
        self.card_values["PARAGRAPHS"].config(text=str(stats["total_paragraphs"]))
        self.card_values["CHARACTERS"].config(text=str(stats["characters_with_spaces"]))
        self.card_values["AVG WORD LEN"].config(text=str(stats["average_word_length"]))

        self.lbl_flesch_score.config(text=f"{readability.get('score', 0)} / 100")
        self.lbl_flesch_ease.config(text=f"Reading Ease: {readability.get('reading_ease', 'N/A')}")
        self.lbl_flesch_grade.config(text=f"Grade Level: {readability.get('grade_level', 'N/A')}")
        self.lbl_flesch_interp.config(text=readability.get("interpretation", ""))

        self.lbl_reading_time.config(text=reading_time.get("reading_time_str", "--"))
        self.lbl_speaking_time.config(text=reading_time.get("speaking_time_str", "--"))

        for label, key in [("Positive", "positive_pct"), ("Neutral", "neutral_pct"),
                            ("Negative", "negative_pct"), ("Sensational", "sensational_pct")]:
            bar, pct_lbl = self.sentiment_bars[label]
            pct = sentiment.get(key, 0.0)
            bar.configure(value=pct)
            pct_lbl.config(text=f"{pct}%")
        self.lbl_predominant_tone.config(text=f"Predominant Tone: {sentiment.get('predominant_tone', '--')}")

        lexical_density = 0.0
        if stats["total_words"] > 0:
            lexical_density = round((stats["unique_words"] / stats["total_words"]) * 100, 1)
        self.lbl_lexical_density.config(text=f"Lexical Density: {lexical_density}%")
        self.lbl_word_lengths.config(
            text=f"Shortest: '{stats['shortest_word']}' | Longest: '{stats['longest_word']}'"
        )

        repeated = stats.get("repeated_adjacent_words", [])
        if repeated:
            self.lbl_repetition.config(
                text=f"{len(repeated)} repeated adjacent word(s) found: {', '.join(repeated[:10])}"
            )
        else:
            self.lbl_repetition.config(text="No repeated adjacent words detected. Clean writing flow.")

    def _refresh_keywords_page(self, sorted_freqs: list):
        for widget in self.keyword_rows_frame.winfo_children():
            widget.destroy()

        if not sorted_freqs:
            self.lbl_keywords_empty = tk.Label(
                self.keyword_rows_frame, text="Analyze content to see ranked keywords.",
                font=("Segoe UI", 9, "italic"), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_CARD
            )
            self.lbl_keywords_empty.pack(anchor="w", pady=8)
            return

        max_count = sorted_freqs[0][1] if sorted_freqs else 1
        for rank, (word, count) in enumerate(sorted_freqs[:30], start=1):
            row = tk.Frame(self.keyword_rows_frame, bg=self.COLOR_CARD)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{rank:>2}.", font=("Segoe UI", 9), fg=self.COLOR_TEXT_MUTED,
                     bg=self.COLOR_CARD, width=3, anchor="e").pack(side=tk.LEFT)
            tk.Label(row, text=word, font=("Segoe UI", 9, "bold"), fg=self.COLOR_TEXT_MAIN,
                     bg=self.COLOR_CARD, width=20, anchor="w").pack(side=tk.LEFT, padx=(6, 8))
            bar = ttk.Progressbar(row, style="Keyword.Horizontal.TProgressbar", orient="horizontal",
                                   mode="determinate", maximum=max_count, value=count)
            bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            tk.Label(row, text=str(count), font=("Segoe UI", 9, "bold"), fg=self.COLOR_PRIMARY,
                     bg=self.COLOR_CARD, width=5, anchor="e").pack(side=tk.LEFT)

    # =========================================================================
    # EXPORT & REPORT GENERATOR
    # =========================================================================
    def export_full_report(self):
        if not self.last_analysis:
            messagebox.showwarning("No Analysis Yet", "Please click 'Analyze Content' before exporting a report.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Full Report", defaultextension=".txt",
            filetypes=[("Text Report (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        report_text = build_full_report(
            title=self.last_analysis["title"],
            text=self.last_analysis["full_text"],
            stats=self.last_analysis["stats"],
            fake_result=(self.last_analysis["score"], self.last_analysis["verdict"], "",
                         self.last_analysis["reasons"], {}),
            readability=self.last_analysis["readability"],
            reading_time=self.last_analysis["reading_time"],
            sentiment=self.last_analysis["sentiment"],
            ranked_keywords=self.last_ranked_keywords,
        )
        success, msg = write_text_file(file_path, report_text)
        if success:
            messagebox.showinfo("Report Exported", msg)
            self.status_lbl.config(text=f"Exported full report to {os.path.basename(file_path)}")
        else:
            messagebox.showerror("Export Failed", msg)

    # =========================================================================
    # DATABASE / SAVED ARCHIVES
    # =========================================================================
    def save_current_analysis_to_db(self):
        if not self.last_analysis:
            messagebox.showwarning("No Analysis Yet", "Please click 'Analyze Content' before saving.")
            return
        if not self.db_connected:
            messagebox.showerror("Database Offline", "Cannot save — database is not connected. Check Settings.")
            return

        a = self.last_analysis
        success, result = self.db.save_analysis(
            title=a["title"], full_text=a["full_text"],
            total_words=a["stats"]["total_words"], total_sentences=a["stats"]["total_sentences"],
            avg_word_length=a["stats"]["average_word_length"], score=a["score"],
            verdict=a["verdict"], reasons_list=a["reasons"]
        )
        if success:
            messagebox.showinfo("Saved", f"Analysis saved to archive (Record #{result}).")
            self.load_database_history()
        else:
            messagebox.showerror("Save Failed", str(result))

    def load_database_history(self):
        if not hasattr(self, "tree"):
            return
        for row in self.tree.get_children():
            self.tree.delete(row)

        filter_val = self.filter_combobox.get() if hasattr(self, "filter_combobox") else "All"
        success, records = self.db.get_all_history(filter_verdict=filter_val)
        if success:
            for rec in records:
                self.tree.insert("", tk.END, values=(
                    rec["id"], rec["created_at"], rec["title"], rec["total_words"],
                    rec["fake_news_score"], rec["verdict"]
                ))

    def _load_selected_history_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to load.")
            return
        record_id = int(self.tree.item(selected[0], "values")[0])

        success, record = self.db.get_history_by_id(record_id)
        if success and record:
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, record["full_text"])
            self._update_live_counts()
            self.run_full_analysis()
            self.show_page("credibility")
            messagebox.showinfo("Record Loaded", f"Loaded Record #{record_id}: '{record['title']}'")
        else:
            messagebox.showerror("Error", f"Could not load record #{record_id}.")

    def _delete_selected_history_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return
        record_id = int(self.tree.item(selected[0], "values")[0])

        if messagebox.askyesno("Confirm Delete", f"Delete Record #{record_id} from the archive?"):
            success, msg = self.db.delete_history_by_id(record_id)
            if success:
                self.load_database_history()
                messagebox.showinfo("Deleted", msg)
            else:
                messagebox.showerror("Error", msg)

    def _open_db_settings_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Database Settings")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.COLOR_BG, padx=20, pady=20)

        tk.Label(dialog, text="Database Connection Settings", font=("Segoe UI", 12, "bold"),
                 bg=self.COLOR_BG, fg=self.COLOR_TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        fields = [("Host:", self.db.host), ("Port:", str(self.db.port)), ("User:", self.db.user),
                  ("Password:", self.db.password), ("Database:", self.db.database)]
        entries = {}
        for label_text, default_val in fields:
            f_row = tk.Frame(dialog, bg=self.COLOR_BG)
            f_row.pack(fill=tk.X, pady=3)
            tk.Label(f_row, text=label_text, width=10, anchor="w", bg=self.COLOR_BG,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)
            ent = tk.Entry(f_row, font=("Segoe UI", 9))
            ent.insert(0, default_val)
            if label_text == "Password:":
                ent.config(show="*")
            ent.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            entries[label_text] = ent

        def test_and_save():
            self.db.host = entries["Host:"].get().strip()
            self.db.port = int(entries["Port:"].get().strip() or 3306)
            self.db.user = entries["User:"].get().strip()
            self.db.password = entries["Password:"].get()
            self.db.database = entries["Database:"].get().strip()

            success, msg = self.db.test_connection()
            if success:
                init_ok, init_msg = self.db.initialize_database()
                if init_ok:
                    self.db_connected = True
                    self.db_status_badge.config(text="🟢 Database Connected", bg=self.COLOR_SUCCESS)
                    self.load_database_history()
                    messagebox.showinfo("Success", "Connected and initialized successfully!", parent=dialog)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", f"Connected, but table creation failed: {init_msg}", parent=dialog)
            else:
                messagebox.showerror("Connection Failed", msg, parent=dialog)

        btn_row = tk.Frame(dialog, bg=self.COLOR_BG)
        btn_row.pack(fill=tk.X, pady=(15, 0))
        tk.Button(btn_row, text="Test & Connect", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY,
                  fg="#FFFFFF", relief=tk.FLAT, padx=12, pady=4, command=test_and_save).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_row, text="Cancel", font=("Segoe UI", 9), bg="#E2E8F0", relief=tk.FLAT,
                  padx=8, pady=4, command=dialog.destroy).pack(side=tk.RIGHT)

    # =========================================================================
    # TEXT TOOLS & MODAL DIALOGS
    # =========================================================================
    def _update_live_counts(self, event=None):
        text = self.text_editor.get("1.0", tk.END)
        if text.endswith("\n"):
            text = text[:-1]
        words = text.split()
        self.editor_count_lbl.config(text=f"Words: {len(words)} | Characters: {len(text)}")

    def _load_preset_sample(self, sample_type: str):
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_news.txt")
        if not os.path.exists(sample_path):
            messagebox.showwarning("File Missing", "Sample content file not found in data/ folder.")
            return
        success, content = read_text_file(sample_path)
        if not success:
            messagebox.showerror("Error", content)
            return

        parts = content.split("=== SAMPLE 2: SUSPICIOUS CLICKBAIT ARTICLE ===")
        if sample_type == "reliable":
            article = parts[0].replace("=== SAMPLE 1: RELIABLE NEWS ARTICLE ===", "").strip()
        else:
            article = parts[1].strip() if len(parts) > 1 else content.strip()

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, article)
        self._update_live_counts()
        self.run_full_analysis()

    def _open_search_dialog(self):
        text = self.get_input_text()
        if not text:
            messagebox.showwarning("Empty", "Please enter text before searching.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Live Search & Highlighting")
        dialog.geometry("360x160")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.configure(bg=self.COLOR_BG, padx=16, pady=16)

        tk.Label(dialog, text="Enter word or phrase to search:", font=("Segoe UI", 9, "bold"),
                 bg=self.COLOR_BG).pack(anchor="w")
        ent = tk.Entry(dialog, font=("Segoe UI", 10))
        ent.pack(fill=tk.X, pady=6)
        ent.focus_set()

        lbl_result = tk.Label(dialog, text="", font=("Segoe UI", 9), bg=self.COLOR_BG, fg=self.COLOR_PRIMARY)
        lbl_result.pack(anchor="w")

        def perform_search():
            target = ent.get().strip()
            self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
            if not target:
                lbl_result.config(text="Please type a word to search.")
                return

            count, _ = search_word_occurrences(self.get_input_text(), target)
            start_pos = "1.0"
            matches_found = 0
            while True:
                start_pos = self.text_editor.search(target, start_pos, nocase=True, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(target)}c"
                self.text_editor.tag_add("search_highlight", start_pos, end_pos)
                start_pos = end_pos
                matches_found += 1

            lbl_result.config(text=f"Matches found: {matches_found} (highlighted in yellow)")

        btn_row = tk.Frame(dialog, bg=self.COLOR_BG)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        tk.Button(btn_row, text="Find Matches", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY,
                  fg="#FFFFFF", relief=tk.FLAT, command=perform_search).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_row, text="Close", bg="#E2E8F0", relief=tk.FLAT, command=dialog.destroy).pack(side=tk.RIGHT)

    def _open_replace_dialog(self):
        text = self.get_input_text()
        if not text:
            messagebox.showwarning("Empty", "Please enter text before replacing words.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Find & Batch Replace")
        dialog.geometry("380x210")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.configure(bg=self.COLOR_BG, padx=16, pady=16)

        tk.Label(dialog, text="Find word:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).pack(anchor="w")
        ent_find = tk.Entry(dialog, font=("Segoe UI", 10))
        ent_find.pack(fill=tk.X, pady=(2, 6))

        tk.Label(dialog, text="Replace with:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).pack(anchor="w")
        ent_replace = tk.Entry(dialog, font=("Segoe UI", 10))
        ent_replace.pack(fill=tk.X, pady=(2, 6))

        def perform_replace():
            find_str = ent_find.get().strip()
            rep_str = ent_replace.get()
            if not find_str:
                messagebox.showwarning("Empty", "Please enter the word to find.", parent=dialog)
                return

            current_text = self.get_input_text()
            updated_text, count = replace_word_in_text(current_text, find_str, rep_str, case_sensitive=False)
            if count > 0:
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert(tk.END, updated_text)
                self._update_live_counts()
                self.run_full_analysis()
                messagebox.showinfo("Replaced", f"Successfully replaced {count} occurrence(s)!", parent=dialog)
                dialog.destroy()
            else:
                messagebox.showinfo("No Matches", f"'{find_str}' was not found in the text.", parent=dialog)

        btn_row = tk.Frame(dialog, bg=self.COLOR_BG)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        tk.Button(btn_row, text="Replace All", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY,
                  fg="#FFFFFF", relief=tk.FLAT, command=perform_replace).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_row, text="Cancel", bg="#E2E8F0", relief=tk.FLAT,
                  command=dialog.destroy).pack(side=tk.RIGHT)

    def _clean_spaces_action(self):
        text = self.get_input_text()
        if not text:
            return
        cleaned = clean_extra_spaces(text)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, cleaned)
        self._update_live_counts()
        self.status_lbl.config(text="Normalized redundant whitespace.")

    def _clean_lines_action(self):
        text = self.get_input_text()
        if not text:
            return
        cleaned = clean_line_breaks(text)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, cleaned)
        self._update_live_counts()
        self.status_lbl.config(text="Cleaned up excess line breaks.")

    def _convert_case_action(self, mode: str):
        text = self.get_input_text()
        if not text:
            return

        if mode == "upper":
            converted = text.upper()
        elif mode == "lower":
            converted = text.lower()
        elif mode == "title":
            converted = text.title()
        elif mode == "sentence":
            converted = format_sentence_case(text)
        else:
            converted = text

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, converted)
        self._update_live_counts()

    # =========================================================================
    # FILE HANDLING (OPEN & SAVE)
    # =========================================================================
    def open_text_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Open Text File", filetypes=[("Text Files (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")]
        )
        if file_path:
            success, content = read_text_file(file_path)
            if success:
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert(tk.END, content)
                self._update_live_counts()
                self.run_full_analysis()
                self.status_lbl.config(text=f"Loaded file: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("File Error", content)

    def save_text_file_dialog(self):
        text = self.get_input_text()
        if not text:
            messagebox.showwarning("Empty", "No text to save.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Save Text File", defaultextension=".txt",
            filetypes=[("Text Files (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")]
        )
        if file_path:
            success, msg = write_text_file(file_path, text)
            if success:
                messagebox.showinfo("File Saved", msg)
                self.status_lbl.config(text=f"Saved file: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Save Error", msg)

    def clear_all(self):
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
        self._update_live_counts()

        for key, lbl in self.card_values.items():
            lbl.config(text="0" if "LEN" not in key else "0.0")

        self.verdict_badge.config(text="READY TO ANALYZE", bg="#E2E8F0", fg=self.COLOR_TEXT_MAIN)
        self.lbl_score_number.config(text="Score: -- / 100", fg=self.COLOR_TEXT_MAIN)
        self.lbl_verdict_summary.config(text="Paste content above and click 'Analyze Content' to begin.")
        self.score_progress.configure(value=0)

        self.txt_fake_output.config(state=tk.NORMAL)
        self.txt_fake_output.delete("1.0", tk.END)
        self.txt_fake_output.config(state=tk.DISABLED)

        self.lbl_flesch_score.config(text="-- / 100")
        self.lbl_flesch_ease.config(text="Reading Ease: --")
        self.lbl_flesch_grade.config(text="Grade Level: --")
        self.lbl_flesch_interp.config(text="Analyze content to see readability results.")
        self.lbl_reading_time.config(text="--")
        self.lbl_speaking_time.config(text="--")
        for label in self.sentiment_bars:
            bar, pct_lbl = self.sentiment_bars[label]
            bar.configure(value=0)
            pct_lbl.config(text="0.0%")
        self.lbl_predominant_tone.config(text="Predominant Tone: --")
        self.lbl_lexical_density.config(text="Lexical Density: --%")
        self.lbl_word_lengths.config(text="Shortest: -- | Longest: --")
        self.lbl_repetition.config(text="No content analyzed yet.")

        self._refresh_keywords_page([])
        self.last_analysis = None
        self.last_ranked_keywords = []
        self.status_lbl.config(text="Cleared all input and analysis results.")