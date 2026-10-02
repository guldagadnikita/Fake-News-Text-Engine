import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import threading
import sys
import os
import datetime
import csv
import io

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

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

from auth_db import (
    register_user, login_user, change_password, update_user_name,
    save_analysis, get_user_history, delete_analysis, clear_user_history,
    get_user_stats, save_report, get_user_reports
)

BG        = "#0B0F19"
SIDEBAR   = "#111827"
CARD      = "#151C2C"
ELEVATED  = "#1C2638"
BORDER    = "#293449"
ACCENT    = "#6366F1"   # indigo
ACCENT2   = "#8B5CF6"   # purple
TEXT1     = "#F9FAFB"
TEXT2     = "#9CA3AF"
TEXT3     = "#6B7280"
COLOR_LOW = "#22C55E"
COLOR_MED = "#F59E0B"
COLOR_HI  = "#EF4444"

def verdict_to_ui_label(verdict: str) -> str:
    """Maps backend verdict to user-facing suspicion label."""
    mapping = {
        "LOW SUSPICION": "LOW SUSPICION",
        "NEEDS VERIFICATION": "MEDIUM SUSPICION",
        "HIGH SUSPICION": "HIGH SUSPICION"
    }
    return mapping.get(verdict, verdict)

def verdict_to_color(verdict: str) -> str:
    if verdict == "LOW SUSPICION":    return COLOR_LOW
    if verdict == "NEEDS VERIFICATION": return COLOR_MED
    return COLOR_HI

class FakeNewsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fake News & Text Processing Engine")
        self.configure(bg=BG)
        self.user_info = None
        self.pages = {}
        self._current_page = None
        
        self.f_title  = font.Font(family="Helvetica", size=20, weight="bold")
        self.f_head   = font.Font(family="Helvetica", size=14, weight="bold")
        self.f_body   = font.Font(family="Helvetica", size=10)
        self.f_small  = font.Font(family="Helvetica", size=9)
        self.f_big    = font.Font(family="Helvetica", size=28, weight="bold")
        self.f_mono   = font.Font(family="Consolas",  size=10)
        
        self._setup_styles()
        self._show_login_state()
        
    def _center(self, w, h):
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}")

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        
        s.configure("TFrame", background=BG)
        s.configure("Sidebar.TFrame", background=SIDEBAR)
        s.configure("Card.TFrame", background=CARD)
        s.configure("Elevated.TFrame", background=ELEVATED)
        
        s.configure("TLabel", background=BG, foreground=TEXT1, font=("Helvetica", 10))
        s.configure("Sidebar.TLabel", background=SIDEBAR, foreground=TEXT1)
        s.configure("Muted.TLabel", background=BG, foreground=TEXT2)
        s.configure("Card.TLabel", background=CARD, foreground=TEXT1)
        s.configure("CardMuted.TLabel", background=CARD, foreground=TEXT2)
        s.configure("Title.TLabel", background=BG, foreground=TEXT1, font=self.f_title)
        s.configure("Header.TLabel", background=BG, foreground=TEXT1, font=self.f_head)
        s.configure("Accent.TLabel", background=BG, foreground=ACCENT)
        
        s.configure("TButton", background=ACCENT, foreground="white", font=("Helvetica", 10), relief="flat", padding=6)
        s.map("TButton", background=[("active", ACCENT2)])
        
        s.configure("Nav.TButton", background=SIDEBAR, foreground=TEXT2, relief="flat", font=("Helvetica", 10))
        s.configure("NavActive.TButton", background=ELEVATED, foreground=TEXT1, relief="flat", font=("Helvetica", 10, "bold"))
        
        s.configure("Danger.TButton", background=COLOR_HI, foreground="white", relief="flat")
        s.configure("Success.TButton", background=COLOR_LOW, foreground="white", relief="flat")
        
        s.configure("TEntry", fieldbackground=ELEVATED, foreground=TEXT1, insertcolor=TEXT1, borderwidth=0, padding=4)
        s.configure("TScrollbar", background=ELEVATED, troughcolor=BG, arrowcolor=TEXT2, borderwidth=0)
        
        s.configure("Treeview", background=CARD, foreground=TEXT1, fieldbackground=CARD, borderwidth=0, font=("Helvetica", 9))
        s.map("Treeview", background=[("selected", ACCENT)])
        s.configure("Treeview.Heading", background=ELEVATED, foreground=TEXT2, font=("Helvetica", 9, "bold"), relief="flat")
        
        s.configure("Horizontal.TProgressbar", troughcolor=ELEVATED, background=ACCENT)

    def _show_login_state(self):
        self._center(460, 560)
        self.login_frame = tk.Frame(self, bg=BG)
        self.login_frame.pack(fill="both", expand=True)
        
        top_frame = tk.Frame(self.login_frame, bg=BG)
        top_frame.pack(pady=(40, 20))
        tk.Label(top_frame, text="🛡️", bg=BG, fg=ACCENT, font=("Helvetica", 36)).pack()
        tk.Label(top_frame, text="FAKE NEWS & TEXT ENGINE", bg=BG, fg=TEXT1, font=("Helvetica", 12, "bold")).pack()
        tk.Label(top_frame, text="Detect • Analyze • Process • Understand", bg=BG, fg=TEXT2, font=("Helvetica", 9)).pack()
        
        self.auth_card = tk.Frame(self.login_frame, bg=CARD, relief="flat", bd=1)
        self.auth_card.pack(padx=40, fill="both", expand=True, pady=(0,40))
        
        self._auth_mode = "login"
        self._build_login_form(self.auth_card)

    def _build_login_form(self, card_frame):
        for widget in card_frame.winfo_children():
            widget.destroy()
        
        container = tk.Frame(card_frame, bg=CARD, padx=30, pady=30)
        container.pack(fill="both", expand=True)
        
        tk.Label(container, text="Sign In", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0, 20))
        
        tk.Label(container, text="Email", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        self.login_email = ttk.Entry(container, font=self.f_body)
        self.login_email.pack(fill="x", pady=(0, 15))
        
        tk.Label(container, text="Password", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        self.login_pwd = ttk.Entry(container, show="*", font=self.f_body)
        self.login_pwd.pack(fill="x", pady=(0, 25))
        
        ttk.Button(container, text="Login", command=self._handle_login).pack(fill="x", pady=(0, 20))
        
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=10)
        tk.Label(container, text="New here?", bg=CARD, fg=TEXT2, font=self.f_small).pack(pady=(10,5))
        tk.Button(container, text="Create Account", bg=CARD, fg=ACCENT, relief="flat", font=self.f_body, activebackground=CARD, activeforeground=ACCENT2, cursor="hand2", command=lambda: self._build_register_form(card_frame)).pack()

    def _build_register_form(self, card_frame):
        for widget in card_frame.winfo_children():
            widget.destroy()
            
        container = tk.Frame(card_frame, bg=CARD, padx=30, pady=20)
        container.pack(fill="both", expand=True)
        
        tk.Label(container, text="Create Account", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0, 15))
        
        tk.Label(container, text="Name", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        self.reg_name = ttk.Entry(container, font=self.f_body)
        self.reg_name.pack(fill="x", pady=(0, 10))
        
        tk.Label(container, text="Email", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        self.reg_email = ttk.Entry(container, font=self.f_body)
        self.reg_email.pack(fill="x", pady=(0, 10))
        
        tk.Label(container, text="Password", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        self.reg_pwd = ttk.Entry(container, show="*", font=self.f_body)
        self.reg_pwd.pack(fill="x", pady=(0, 10))
        
        tk.Label(container, text="Confirm Password", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        self.reg_pwd2 = ttk.Entry(container, show="*", font=self.f_body)
        self.reg_pwd2.pack(fill="x", pady=(0, 20))
        
        ttk.Button(container, text="Register", command=self._handle_register).pack(fill="x", pady=(0, 15))
        
        tk.Button(container, text="Back to Login", bg=CARD, fg=ACCENT, relief="flat", font=self.f_body, activebackground=CARD, activeforeground=ACCENT2, cursor="hand2", command=lambda: self._build_login_form(card_frame)).pack()

    def _handle_login(self):
        email = self.login_email.get().strip()
        pwd = self.login_pwd.get()
        if not email or not pwd:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        success, res = login_user(email, pwd)
        if success:
            self.user_info = res
            self._show_main_state()
        else:
            messagebox.showerror("Error", res)

    def _handle_register(self):
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        pwd = self.reg_pwd.get()
        pwd2 = self.reg_pwd2.get()
        
        if not name or not email or not pwd or not pwd2:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        if "@" not in email:
            messagebox.showerror("Error", "Invalid email format.")
            return
        if len(pwd) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters.")
            return
        if pwd != pwd2:
            messagebox.showerror("Error", "Passwords do not match.")
            return
            
        success, res = register_user(name, email, pwd)
        if success:
            messagebox.showinfo("Success", "Account created! Please log in.")
            self._build_login_form(self.auth_card)
        else:
            messagebox.showerror("Error", res)

    def _show_main_state(self):
        self.login_frame.destroy()
        self._center(1280, 820)
        
        self._main = tk.Frame(self, bg=BG)
        self._main.pack(fill="both", expand=True)
        
        self._sidebar_frame = tk.Frame(self._main, bg=SIDEBAR, width=220)
        self._sidebar_frame.pack(side="left", fill="y")
        self._sidebar_frame.pack_propagate(False)
        
        self._content = tk.Frame(self._main, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)
        
        self._build_sidebar()
        self._show_page("home")

    def _build_sidebar(self):
        sidebar = self._sidebar_frame
        
        logo_frame = tk.Frame(sidebar, bg=SIDEBAR)
        logo_frame.pack(fill="x", pady=20)
        tk.Label(logo_frame, text="🛡️", bg=SIDEBAR, fg=ACCENT, font=("Helvetica",18)).pack(side="left", padx=(16,6))
        tk.Label(logo_frame, text="FAKE NEWS\n& TEXT ENGINE", bg=SIDEBAR, fg=TEXT1, font=("Helvetica",9,"bold"), justify="left").pack(side="left")
        
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x")
        
        nav_frame = tk.Frame(sidebar, bg=SIDEBAR)
        nav_frame.pack(fill="x", pady=10)
        
        self._nav_buttons = {}
        nav_items = [
            ("🏠", "Home", "home"),
            ("📊", "Dashboard", "dashboard"),
            ("🔍", "Credibility Checker", "detection"),
            ("📝", "Text Processing", "processing"),
            ("📈", "Analysis", "analysis"),
            ("🔄", "Comparison", "comparison"),
            ("📜", "History", "history"),
            ("⚙️", "Settings", "settings"),
        ]
        for icon, label, key in nav_items:
            btn = tk.Button(nav_frame, text=f"  {icon}  {label}", anchor="w",
                bg=SIDEBAR, fg=TEXT2, activebackground=ELEVATED, activeforeground=TEXT1,
                relief="flat", font=("Helvetica",10), cursor="hand2", bd=0,
                padx=8, pady=10, command=lambda k=key: self._show_page(k))
            btn.pack(fill="x")
            self._nav_buttons[key] = btn
            
        tk.Frame(sidebar, bg=SIDEBAR).pack(fill="both", expand=True)
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x")
        
        tk.Label(sidebar, text="Signed in as", bg=SIDEBAR, fg=TEXT3, font=("Helvetica",8)).pack(anchor="w", padx=16, pady=(8,0))
        self._user_label = tk.Label(sidebar, text=self.user_info["name"], bg=SIDEBAR, fg=TEXT1, font=("Helvetica",9,"bold"))
        self._user_label.pack(anchor="w", padx=16, pady=(0,4))
        
        tk.Button(sidebar, text="Sign Out", bg=ELEVATED, fg=TEXT2, relief="flat",
            font=("Helvetica",9), cursor="hand2", command=self._logout, padx=10, pady=6).pack(fill="x", padx=12, pady=(0,12))

    def _show_page(self, key):
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.config(bg=ELEVATED, fg=TEXT1, font=("Helvetica",10,"bold"))
            else:
                btn.config(bg=SIDEBAR, fg=TEXT2, font=("Helvetica",10))
                
        if self._current_page:
            self._current_page.pack_forget()
            
        if key not in self.pages:
            self.pages[key] = self._create_page(key)
            
        self._current_page = self.pages[key]
        self._current_page.pack(fill="both", expand=True)
        
        if hasattr(self._current_page, "refresh"):
            self._current_page.refresh()

    def _create_page(self, key):
        frame = tk.Frame(self._content, bg=BG)
        build_methods = {
            "home": self._build_home,
            "dashboard": self._build_dashboard,
            "detection": self._build_detection,
            "processing": self._build_processing,
            "analysis": self._build_analysis,
            "comparison": self._build_comparison,
            "history": self._build_history,
            "settings": self._build_settings
        }
        if key in build_methods:
            build_methods[key](frame)
        return frame

    def _card(self, parent, padx=16, pady=12):
        outer = tk.Frame(parent, bg=CARD, padx=padx, pady=pady)
        return outer

    def _metric_card(self, parent, label, value, color=ACCENT):
        f = tk.Frame(parent, bg=CARD, padx=16, pady=12)
        tk.Frame(f, bg=color, width=3).pack(side="left", fill="y", padx=(0,10))
        inner = tk.Frame(f, bg=CARD)
        inner.pack(side="left", fill="both", expand=True)
        tk.Label(inner, text=label.upper(), bg=CARD, fg=TEXT2, font=("Helvetica",8)).pack(anchor="w")
        tk.Label(inner, text=str(value), bg=CARD, fg=TEXT1, font=("Helvetica",20,"bold")).pack(anchor="w")
        return f

    def _scrollable_frame(self, parent):
        outer = tk.Frame(parent, bg=BG)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=parent.winfo_width())
        outer.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return outer, inner

    def _build_home(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        hero = tk.Frame(inner, bg=BG, pady=60)
        hero.pack(fill="x")
        tk.Label(hero, text="FAKE NEWS &\nTEXT PROCESSING ENGINE", bg=BG, fg=TEXT1, font=self.f_big).pack()
        tk.Label(hero, text="Detect • Analyze • Process • Understand", bg=BG, fg=ACCENT, font=self.f_head).pack(pady=(10,20))
        tk.Label(hero, text="A comprehensive suite of tools for evaluating text credibility, readability, and structural elements.", bg=BG, fg=TEXT2, font=self.f_body).pack()
        
        btn_row = tk.Frame(hero, bg=BG)
        btn_row.pack(pady=30)
        tk.Button(btn_row, text="🔍 Start Analysis", bg=ACCENT, fg="white", font=self.f_body, relief="flat", padx=20, pady=10, cursor="hand2", command=lambda: self._show_page("detection")).pack(side="left", padx=10)
        tk.Button(btn_row, text="📊 Dashboard", bg=ELEVATED, fg=TEXT1, font=self.f_body, relief="flat", padx=20, pady=10, cursor="hand2", command=lambda: self._show_page("dashboard")).pack(side="left", padx=10)
        
        features_frame = tk.Frame(inner, bg=BG, padx=40)
        features_frame.pack(fill="x", pady=20)
        
        features = [
            ("🔍", "Credibility Checker", "Evaluate the trust score of articles."),
            ("📝", "Text Processing", "Clean and format raw text easily."),
            ("📈", "Analysis Dashboard", "Track your statistics and history."),
            ("🔄", "Text Comparison", "Compare two texts for similarity."),
            ("🧠", "Sentiment & Readability", "Understand the tone and difficulty of text."),
            ("📜", "Detailed Reports", "Export complete reports for your records.")
        ]
        
        grid = tk.Frame(features_frame, bg=BG)
        grid.pack()
        
        for i, (icon, title, desc) in enumerate(features):
            row = i // 3
            col = i % 3
            card = self._card(grid)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            tk.Label(card, text=icon, bg=CARD, fg=ACCENT, font=("Helvetica", 24)).pack(pady=(0,10))
            tk.Label(card, text=title, bg=CARD, fg=TEXT1, font=self.f_head).pack()
            tk.Label(card, text=desc, bg=CARD, fg=TEXT2, font=self.f_small, wraplength=200).pack(pady=(5,0))
            
        tk.Label(inner, text="* This tool uses rule-based heuristic checks. Always verify critical information from trusted sources.", bg=BG, fg=TEXT3, font=self.f_small).pack(pady=40)

    def _build_dashboard(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        top = tk.Frame(inner, bg=BG, padx=30, pady=20)
        top.pack(fill="x")
        
        greeting = "Welcome"
        hour = datetime.datetime.now().hour
        if hour < 12: greeting = "Good morning"
        elif hour < 18: greeting = "Good afternoon"
        else: greeting = "Good evening"
        
        self.dash_greeting = tk.Label(top, text=f"{greeting}, {self.user_info['name']}", bg=BG, fg=TEXT1, font=self.f_title)
        self.dash_greeting.pack(anchor="w")
        self.dash_date = tk.Label(top, text=datetime.datetime.now().strftime("%A, %B %d, %Y"), bg=BG, fg=TEXT2, font=self.f_body)
        self.dash_date.pack(anchor="w")
        
        self.metrics_row = tk.Frame(inner, bg=BG, padx=25)
        self.metrics_row.pack(fill="x", pady=10)
        
        self.chart_tree_row = tk.Frame(inner, bg=BG, padx=25)
        self.chart_tree_row.pack(fill="both", expand=True, pady=10)
        
        def refresh_dashboard():
            self.dash_greeting.config(text=f"{greeting}, {self.user_info['name']}")
            for w in self.metrics_row.winfo_children(): w.destroy()
            for w in self.chart_tree_row.winfo_children(): w.destroy()
            
            stats = get_user_stats(self.user_info["id"])
            metrics = [
                ("Total Analyzed", stats.get("total_analyses",0), ACCENT),
                ("Low Suspicion",  stats.get("reliable",0), COLOR_LOW),
                ("Medium Suspicion",stats.get("needs_verification",0), COLOR_MED),
                ("High Suspicion", stats.get("suspicious",0), COLOR_HI),
            ]
            for label, val, col in metrics:
                card = self._metric_card(self.metrics_row, label, val, col)
                card.pack(side="left", fill="both", expand=True, padx=5)
                
            left_col = tk.Frame(self.chart_tree_row, bg=BG)
            left_col.pack(side="left", fill="both", expand=True, padx=5)
            
            tree_card = self._card(left_col)
            tree_card.pack(fill="both", expand=True)
            tk.Label(tree_card, text="Recent Analyses", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0,10))
            
            cols = ("Date", "Preview", "Score", "Level", "Words")
            tree = ttk.Treeview(tree_card, columns=cols, show="headings", height=6)
            tree.heading("Date", text="Date")
            tree.heading("Preview", text="Preview")
            tree.heading("Score", text="Score")
            tree.heading("Level", text="Level")
            tree.heading("Words", text="Words")
            
            tree.column("Date", width=80)
            tree.column("Preview", width=300)
            tree.column("Score", width=60)
            tree.column("Level", width=120)
            tree.column("Words", width=60)
            tree.pack(fill="both", expand=True)
            
            history = get_user_history(self.user_info["id"])
            for rec in history[:5]:
                tree.insert("", "end", values=(rec["created_at"][:10], rec["text_preview"][:40]+"...",
                    rec["score"], verdict_to_ui_label(rec["verdict"]), rec["word_count"]))
                    
            if HAS_MATPLOTLIB and sum([stats.get("reliable",0), stats.get("needs_verification",0), stats.get("suspicious",0)]) > 0:
                right_col = tk.Frame(self.chart_tree_row, bg=BG)
                right_col.pack(side="right", fill="both", expand=True, padx=5)
                chart_card = self._card(right_col)
                chart_card.pack(fill="both", expand=True)
                tk.Label(chart_card, text="Suspicion Distribution", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w")
                
                fig = Figure(figsize=(4, 3), dpi=100, facecolor=CARD)
                ax = fig.add_subplot(111)
                ax.set_facecolor(CARD)
                
                labels = ['Low', 'Medium', 'High']
                sizes = [stats.get("reliable",0), stats.get("needs_verification",0), stats.get("suspicious",0)]
                colors = [COLOR_LOW, COLOR_MED, COLOR_HI]
                
                valid = [(l,s,c) for l,s,c in zip(labels, sizes, colors) if s > 0]
                if valid:
                    v_labels, v_sizes, v_colors = zip(*valid)
                    wedges, texts, autotexts = ax.pie(v_sizes, labels=v_labels, colors=v_colors, autopct='%1.1f%%',
                                                      wedgeprops=dict(width=0.4, edgecolor=CARD), textprops=dict(color=TEXT1))
                    
                    canvas = FigureCanvasTkAgg(fig, master=chart_card)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
            
        frame.refresh = refresh_dashboard
        refresh_dashboard()

    def _build_detection(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        top = tk.Frame(inner, bg=BG, padx=30, pady=20)
        top.pack(fill="x")
        tk.Label(top, text="🔍 News Credibility Checker", bg=BG, fg=TEXT1, font=self.f_title).pack(anchor="w")
        tk.Label(top, text="Check the credibility of news articles using our keyword and rule-based detection engine.", bg=BG, fg=TEXT2, font=self.f_body).pack(anchor="w", pady=(5,0))
        
        q_row = tk.Frame(inner, bg=BG, padx=30)
        q_row.pack(fill="x", pady=10)
        
        def load_sample(t):
            self._det_text.delete("1.0", "end")
            self._det_text.insert("1.0", t)
            
        def open_file():
            fpath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if fpath:
                content = read_text_file(fpath)
                load_sample(content)
                
        sample_bad = "SHOCKING EXPOSED!!! The secret TRUTH they don't want you to know! Click here to see what happens next! You will not believe this fake story that is completely fabricated and lacks any credible sources whatsoever!!!"
        sample_good = "According to a recent report by the Associated Press, the local city council has voted to approve the new infrastructure budget. The study, published in the Journal of Economics, details the expected impact on community development over the next decade."
        
        tk.Button(q_row, text="Load Suspicious Sample", bg=ELEVATED, fg=TEXT1, relief="flat", font=self.f_small, command=lambda: load_sample(sample_bad)).pack(side="left", padx=(0,10))
        tk.Button(q_row, text="Load Reliable Sample", bg=ELEVATED, fg=TEXT1, relief="flat", font=self.f_small, command=lambda: load_sample(sample_good)).pack(side="left", padx=10)
        tk.Button(q_row, text="Open File", bg=ELEVATED, fg=TEXT1, relief="flat", font=self.f_small, command=open_file).pack(side="left", padx=10)
        
        text_frame = tk.Frame(inner, bg=BG, padx=30)
        text_frame.pack(fill="both", expand=True)
        
        self._det_text = tk.Text(text_frame, bg=ELEVATED, fg=TEXT1, insertbackground=TEXT1,
            font=self.f_mono, height=10, relief="flat", padx=12, pady=8, wrap="word",
            bd=1, highlightthickness=1, highlightbackground=BORDER)
        self._det_text.pack(fill="both", expand=True)
        self._det_text.insert("1.0", "Paste a news headline or article here to check its credibility...")
        
        btn_row = tk.Frame(inner, bg=BG, padx=30)
        btn_row.pack(fill="x", pady=15)
        
        self._det_btn = tk.Button(btn_row, text="🔍 Analyze Text", bg=ACCENT, fg="white", font=self.f_head, relief="flat", padx=20, pady=8, command=self._run_detection)
        self._det_btn.pack(side="left", padx=(0,15))
        
        tk.Button(btn_row, text="✕ Clear", bg=ELEVATED, fg=TEXT1, font=self.f_body, relief="flat", padx=15, pady=8, command=lambda: self._det_text.delete("1.0", "end")).pack(side="left")
        
        self._det_status = tk.Label(btn_row, text="", bg=BG, fg=ACCENT, font=self.f_body)
        self._det_status.pack(side="left", padx=20)
        
        self._det_results_frame = tk.Frame(inner, bg=BG, padx=30, pady=10)
        self._det_results_frame.pack(fill="both", expand=True)

    def _run_detection(self):
        text = self._det_text.get("1.0", "end-1c").strip()
        placeholder = "Paste a news headline or article here..."
        if not text or text == placeholder:
            messagebox.showwarning("Input Required", "Please enter some text before analyzing.")
            return
        if len(text) < 10:
            messagebox.showwarning("Too Short", "Text is too short for meaningful analysis.")
            return
            
        self._det_status.config(text="⏳ Analyzing text patterns...", fg=ACCENT)
        self._det_btn.config(state="disabled")
        threading.Thread(target=self._detection_worker, args=(text,), daemon=True).start()

    def _detection_worker(self, text):
        try:
            score, verdict, color_hex, reasons, details = calculate_fake_news_score(text)
            stats = calculate_text_statistics(text)
            readability = calculate_readability_score(text)
            rt = estimate_reading_time(stats["total_words"])
            sentiment = analyze_sentiment(text)
            freq = get_word_frequencies(tokenize_words(text))
            sorted_freq, _, _, _ = bubble_sort_frequencies(freq)
            
            save_analysis(self.user_info["id"], text, score, verdict, stats["total_words"])
            
            self.after(0, self._display_detection_results, score, verdict, color_hex, reasons, details, stats, readability, rt, sentiment, sorted_freq, text)
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Analysis Error", str(e)))
        finally:
            self.after(0, lambda: (
                self._det_status.config(text=""),
                self._det_btn.config(state="normal")
            ))

    def _display_detection_results(self, score, verdict, color_hex, reasons, details, stats, readability, rt, sentiment, sorted_freq, text):
        for w in self._det_results_frame.winfo_children(): w.destroy()
        
        top_cards = tk.Frame(self._det_results_frame, bg=BG)
        top_cards.pack(fill="x", pady=10)
        
        vc = verdict_to_color(verdict)
        
        left_card = tk.Frame(top_cards, bg=CARD, padx=20, pady=20)
        left_card.pack(side="left", fill="y", expand=True, padx=(0,10))
        
        tk.Frame(left_card, bg=vc, width=4).pack(side="left", fill="y", padx=(0,12))
        inner = tk.Frame(left_card, bg=CARD)
        inner.pack(side="left", fill="both", expand=True)
        tk.Label(inner, text="TRUST SCORE", bg=CARD, fg=TEXT2, font=("Helvetica",9)).pack()
        tk.Label(inner, text=str(score), bg=CARD, fg=vc, font=("Helvetica",48,"bold")).pack()
        tk.Label(inner, text="out of 100", bg=CARD, fg=TEXT2, font=("Helvetica",9)).pack()
        
        badge_text = verdict_to_ui_label(verdict)
        tk.Label(inner, text=badge_text, bg=vc, fg="white", font=("Helvetica",9,"bold"), padx=12, pady=4).pack(pady=8)
        
        pb = ttk.Progressbar(inner, value=score, maximum=100, length=200)
        pb.pack(pady=4)
        
        right_card = tk.Frame(top_cards, bg=CARD, padx=20, pady=20)
        right_card.pack(side="left", fill="both", expand=True, padx=(10,0))
        tk.Label(right_card, text="Score Breakdown", bg=CARD, fg=TEXT1, font=("Helvetica",12,"bold")).pack(anchor="w", pady=(0,10))
        
        rule_rows = [
            (details.get("suspicious_points",0) > 0,
             "Suspicious Keywords",
             f"+{details.get('suspicious_points',0)} pts — {len(details.get('suspicious_matches',[]))} match(es)"),
            (details.get("clickbait_points",0) > 0,
             "Clickbait Phrases",
             f"+{details.get('clickbait_points',0)} pts — {len(details.get('clickbait_matches',[]))} match(es)"),
            (details.get("punct_points",0) > 0,
             "Excessive Punctuation",
             f"+{details.get('punct_points',0)} pts — {details.get('punct_clusters',0)} cluster(s)"),
            (details.get("caps_points",0) > 0,
             "All-Caps Ratio",
             f"+{details.get('caps_points',0)} pts — {details.get('caps_ratio',0)}% ALL-CAPS"),
            (details.get("brevity_points",0) > 0,
             "Brief Content",
             f"+{details.get('brevity_points',0)} pts — {details.get('total_words',0)} words"),
            (True,
             "Credible Attribution",
             f"-{details.get('credible_reduction',0)} pts" if details.get('credible_reduction',0)>0 else "No attribution found (+0 pts)"),
        ]

        for flagged, rule_name, detail_text in rule_rows:
            row_f = tk.Frame(right_card, bg=CARD)
            row_f.pack(fill="x", pady=3)
            
            if rule_name == "Credible Attribution":
                icon, col = ("✓", COLOR_LOW) if details.get("credible_reduction",0)>0 else ("⚠", COLOR_MED)
            else:
                icon, col = ("⚠", COLOR_HI) if flagged else ("✓", COLOR_LOW)
                
            tk.Label(row_f, text=icon, bg=CARD, fg=col, font=("Helvetica",11,"bold"), width=2).pack(side="left")
            name_f = tk.Frame(row_f, bg=CARD)
            name_f.pack(side="left", fill="x", expand=True)
            tk.Label(name_f, text=rule_name, bg=CARD, fg=TEXT1, font=("Helvetica",9,"bold"), anchor="w").pack(anchor="w")
            tk.Label(name_f, text=detail_text, bg=CARD, fg=TEXT2, font=("Helvetica",8), anchor="w").pack(anchor="w")

        tk.Frame(right_card, bg=BORDER, height=1).pack(fill="x", pady=8)
        total_row = tk.Frame(right_card, bg=CARD)
        total_row.pack(fill="x")
        tk.Label(total_row, text="Overall Suspicion Score", bg=CARD, fg=TEXT2, font=("Helvetica",9,"bold")).pack(side="left")
        tk.Label(total_row, text=f"{score} / 100", bg=CARD, fg=vc, font=("Helvetica",13,"bold")).pack(side="right")
        
        stats_row = tk.Frame(self._det_results_frame, bg=BG)
        stats_row.pack(fill="x", pady=10)
        
        avg_wps = round(stats["total_words"] / max(stats["total_sentences"],1), 1)
        grade = readability.get("grade_level", "N/A")
        stat_items = [
            ("Word Count", stats["total_words"]),
            ("Sentences", stats["total_sentences"]),
            ("Paragraphs", stats["total_paragraphs"]),
            ("Avg Words/Sent", avg_wps),
            ("Reading Level", grade),
        ]
        
        for label, val in stat_items:
            sc = tk.Frame(stats_row, bg=CARD, padx=12, pady=10)
            sc.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(sc, text=str(val), bg=CARD, fg=TEXT1, font=("Helvetica",14,"bold")).pack()
            tk.Label(sc, text=label, bg=CARD, fg=TEXT2, font=("Helvetica",8)).pack()
            
        tk.Label(self._det_results_frame, text="Detailed Feedback", bg=BG, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(10,5))
        reason_text = tk.Text(self._det_results_frame, bg=ELEVATED, fg=TEXT1, font=self.f_small, height=5,
            wrap="word", relief="flat", padx=10, pady=8, state="normal", bd=0)
        reason_text.pack(fill="x")
        for r in reasons:
            reason_text.insert("end", r + "\n")
        reason_text.config(state="disabled")
        
        btn_frame = tk.Frame(self._det_results_frame, bg=BG)
        btn_frame.pack(fill="x", pady=15)
        
        def _export_report_action():
            report_str = build_full_report("News Analysis", text, stats,
                (score, verdict, color_hex, reasons, details), readability, sentiment,
                sorted_freq[:15] if sorted_freq else [])
            fpath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")])
            if fpath:
                try:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(report_str)
                    save_report(self.user_info["id"], f"Analysis {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", report_str)
                    messagebox.showinfo("Saved", f"Report saved to {fpath}")
                except Exception as e:
                    messagebox.showerror("Export Error", str(e))
                    
        tk.Button(btn_frame, text="Export Full Report", bg=ACCENT, fg="white", font=self.f_body, relief="flat", padx=15, pady=8, command=_export_report_action).pack(side="right")

    def _build_processing(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        tk.Label(inner, text="📝 Text Processing", bg=BG, fg=TEXT1, font=self.f_title).pack(anchor="w", padx=30, pady=20)
        
        in_frame = tk.Frame(inner, bg=BG, padx=30)
        in_frame.pack(fill="x")
        tk.Label(in_frame, text="Input Text", bg=BG, fg=TEXT2, font=self.f_small).pack(anchor="w")
        in_text = tk.Text(in_frame, bg=ELEVATED, fg=TEXT1, insertbackground=TEXT1, font=self.f_mono, height=8, relief="flat", padx=10, pady=10)
        in_text.pack(fill="x", pady=(5,15))
        
        btn_frame = tk.Frame(inner, bg=BG, padx=30)
        btn_frame.pack(fill="x", pady=5)
        
        out_frame = tk.Frame(inner, bg=BG, padx=30)
        out_frame.pack(fill="x", pady=15)
        tk.Label(out_frame, text="Output Text", bg=BG, fg=TEXT2, font=self.f_small).pack(anchor="w")
        out_text = tk.Text(out_frame, bg=ELEVATED, fg=TEXT1, font=self.f_mono, height=8, relief="flat", padx=10, pady=10)
        out_text.pack(fill="x", pady=(5,0))
        
        def set_out(t):
            out_text.config(state="normal")
            out_text.delete("1.0", "end")
            out_text.insert("1.0", t)
            out_text.config(state="disabled")
            
        def do_op(op_name):
            txt = in_text.get("1.0", "end-1c")
            if not txt: return
            if op_name == "upper": set_out(txt.upper())
            elif op_name == "lower": set_out(txt.lower())
            elif op_name == "title": set_out(txt.title())
            elif op_name == "sentence": set_out(format_sentence_case(txt))
            elif op_name == "spaces": set_out(clean_extra_spaces(txt))
            elif op_name == "lines": set_out(clean_line_breaks(txt))
            
        ops = [("UPPER", "upper"), ("lower", "lower"), ("Title", "title"), ("Sentence", "sentence"), ("Clean Spaces", "spaces"), ("Clean Lines", "lines")]
        for label, op in ops:
            tk.Button(btn_frame, text=label, bg=ELEVATED, fg=TEXT1, font=self.f_body, relief="flat", padx=10, command=lambda o=op: do_op(o)).pack(side="left", padx=(0,10))
            
        sr_frame = self._card(inner)
        sr_frame.pack(fill="x", padx=30, pady=20)
        tk.Label(sr_frame, text="Search & Replace", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0,10))
        
        sr_inputs = tk.Frame(sr_frame, bg=CARD)
        sr_inputs.pack(fill="x")
        
        tk.Label(sr_inputs, text="Search for:", bg=CARD, fg=TEXT2).pack(side="left")
        s_ent = ttk.Entry(sr_inputs, font=self.f_body, width=15)
        s_ent.pack(side="left", padx=10)
        
        s_res = tk.Label(sr_inputs, text="", bg=CARD, fg=ACCENT)
        s_res.pack(side="left", padx=10)
        
        def do_search():
            q = s_ent.get()
            txt = out_text.get("1.0", "end-1c") if out_text.get("1.0", "end-1c") else in_text.get("1.0", "end-1c")
            if not q or not txt: return
            count = len(search_word_occurrences(txt, q))
            s_res.config(text=f"Found {count} occurrences")
            
        tk.Button(sr_inputs, text="Search", bg=ELEVATED, fg=TEXT1, relief="flat", padx=10, command=do_search).pack(side="left")
        
        sr_inputs2 = tk.Frame(sr_frame, bg=CARD)
        sr_inputs2.pack(fill="x", pady=(15,0))
        tk.Label(sr_inputs2, text="Replace with:", bg=CARD, fg=TEXT2).pack(side="left")
        r_ent = ttk.Entry(sr_inputs2, font=self.f_body, width=15)
        r_ent.pack(side="left", padx=(5,10))
        
        def do_replace():
            q = s_ent.get()
            r = r_ent.get()
            txt = out_text.get("1.0", "end-1c") if out_text.get("1.0", "end-1c") else in_text.get("1.0", "end-1c")
            if not q or not txt: return
            new_txt = replace_word_in_text(txt, q, r)
            set_out(new_txt)
            s_res.config(text="Replaced")
            
        tk.Button(sr_inputs2, text="Replace All", bg=ACCENT, fg="white", relief="flat", padx=10, command=do_replace).pack(side="left")

    def _build_analysis(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        tk.Label(inner, text="📈 Analytics", bg=BG, fg=TEXT1, font=self.f_title).pack(anchor="w", padx=30, pady=20)
        
        self.an_charts_frame = tk.Frame(inner, bg=BG, padx=30)
        self.an_charts_frame.pack(fill="x", pady=10)
        
        self.an_stats_frame = tk.Frame(inner, bg=BG, padx=30)
        self.an_stats_frame.pack(fill="x", pady=10)
        
        self.an_tree_frame = self._card(inner)
        self.an_tree_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        def refresh_analysis():
            for w in self.an_charts_frame.winfo_children(): w.destroy()
            for w in self.an_stats_frame.winfo_children(): w.destroy()
            for w in self.an_tree_frame.winfo_children(): w.destroy()
            
            history = get_user_history(self.user_info["id"])
            if not history:
                tk.Label(self.an_charts_frame, text="No analysis history available yet.", bg=BG, fg=TEXT2).pack()
                return
                
            scores = [r["score"] for r in history]
            avg_score = round(sum(scores)/len(scores), 1)
            
            sc_cards = [
                ("Total Analyses", len(history)),
                ("Average Score", avg_score),
                ("Highest Score", max(scores)),
                ("Lowest Score", min(scores))
            ]
            
            for lbl, val in sc_cards:
                c = self._metric_card(self.an_stats_frame, lbl, val)
                c.pack(side="left", fill="both", expand=True, padx=5)
                
            if HAS_MATPLOTLIB:
                fig = Figure(figsize=(8, 4), dpi=100, facecolor=BG)
                
                low = sum(1 for r in history if r["verdict"] == "LOW SUSPICION")
                med = sum(1 for r in history if r["verdict"] == "NEEDS VERIFICATION")
                hi = sum(1 for r in history if r["verdict"] == "HIGH SUSPICION")
                
                ax1 = fig.add_subplot(121)
                ax1.set_facecolor(BG)
                labels = ['Low', 'Medium', 'High']
                sizes = [low, med, hi]
                colors = [COLOR_LOW, COLOR_MED, COLOR_HI]
                valid = [(l,s,c) for l,s,c in zip(labels, sizes, colors) if s > 0]
                if valid:
                    v_labels, v_sizes, v_colors = zip(*valid)
                    ax1.pie(v_sizes, labels=v_labels, colors=v_colors, autopct='%1.1f%%', wedgeprops=dict(width=0.4, edgecolor=BG), textprops=dict(color=TEXT1))
                    ax1.set_title("Distribution", color=TEXT1)
                    
                ax2 = fig.add_subplot(122)
                ax2.set_facecolor(BG)
                ax2.bar(['Low', 'Med', 'High'], [low, med, hi], color=[COLOR_LOW, COLOR_MED, COLOR_HI])
                ax2.set_title("Counts", color=TEXT1)
                ax2.tick_params(colors=TEXT1)
                for spine in ax2.spines.values():
                    spine.set_color(BORDER)
                    
                canvas = FigureCanvasTkAgg(fig, master=self.an_charts_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
                
            tk.Label(self.an_tree_frame, text="History Summary", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0,10))
            cols = ("Date", "Score", "Level", "Words")
            tree = ttk.Treeview(self.an_tree_frame, columns=cols, show="headings", height=8)
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=100)
            tree.pack(fill="both", expand=True)
            for rec in history[:20]:
                tree.insert("", "end", values=(rec["created_at"][:10], rec["score"], verdict_to_ui_label(rec["verdict"]), rec["word_count"]))
                
        frame.refresh = refresh_analysis

    def _build_comparison(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        tk.Label(inner, text="🔄 Text Comparison", bg=BG, fg=TEXT1, font=self.f_title).pack(anchor="w", padx=30, pady=20)
        
        txt_row = tk.Frame(inner, bg=BG, padx=30)
        txt_row.pack(fill="x")
        
        f_a = tk.Frame(txt_row, bg=BG)
        f_a.pack(side="left", fill="both", expand=True, padx=(0,10))
        tk.Label(f_a, text="Text A", bg=BG, fg=TEXT1, font=self.f_head).pack(anchor="w")
        txt_a = tk.Text(f_a, bg=ELEVATED, fg=TEXT1, insertbackground=TEXT1, font=self.f_mono, height=12, relief="flat", padx=10, pady=10)
        txt_a.pack(fill="both", expand=True, pady=(5,0))
        
        f_b = tk.Frame(txt_row, bg=BG)
        f_b.pack(side="left", fill="both", expand=True, padx=(10,0))
        tk.Label(f_b, text="Text B", bg=BG, fg=TEXT1, font=self.f_head).pack(anchor="w")
        txt_b = tk.Text(f_b, bg=ELEVATED, fg=TEXT1, insertbackground=TEXT1, font=self.f_mono, height=12, relief="flat", padx=10, pady=10)
        txt_b.pack(fill="both", expand=True, pady=(5,0))
        
        btn_row = tk.Frame(inner, bg=BG, padx=30)
        btn_row.pack(fill="x", pady=20)
        
        res_card = self._card(inner)
        res_card.pack(fill="x", padx=30, pady=10)
        
        def do_compare():
            for w in res_card.winfo_children(): w.destroy()
            a = txt_a.get("1.0", "end-1c").strip()
            b = txt_b.get("1.0", "end-1c").strip()
            if not a or not b:
                messagebox.showwarning("Input Required", "Please provide both Text A and Text B.")
                return
            res = compare_texts(a, b)
            
            tk.Label(res_card, text="Comparison Results", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0,15))
            
            sim_frame = tk.Frame(res_card, bg=CARD)
            sim_frame.pack(fill="x", pady=5)
            tk.Label(sim_frame, text=f"Similarity: {res['similarity_pct']}%", bg=CARD, fg=TEXT1, font=("Helvetica",16,"bold")).pack(anchor="w")
            tk.Label(sim_frame, text=res['similarity_label'], bg=CARD, fg=ACCENT, font=self.f_body).pack(anchor="w")
            
            pb = ttk.Progressbar(sim_frame, value=res['similarity_pct'], maximum=100, length=400)
            pb.pack(anchor="w", pady=(5,15))
            
            stats_frame = tk.Frame(res_card, bg=CARD)
            stats_frame.pack(fill="x")
            items = [
                ("Words in A", res['word_count_a']),
                ("Words in B", res['word_count_b']),
                ("Common Words", res['common_words_count']),
                ("Unique to A", res['unique_to_a_count']),
                ("Unique to B", res['unique_to_b_count'])
            ]
            for lbl, val in items:
                c = tk.Frame(stats_frame, bg=CARD, padx=10)
                c.pack(side="left")
                tk.Label(c, text=str(val), bg=CARD, fg=TEXT1, font=("Helvetica",14,"bold")).pack()
                tk.Label(c, text=lbl, bg=CARD, fg=TEXT2, font=self.f_small).pack()
                
        tk.Button(btn_row, text="🔄 Compare Texts", bg=ACCENT, fg="white", font=self.f_head, relief="flat", padx=20, pady=8, command=do_compare).pack(side="left")
        tk.Button(btn_row, text="✕ Clear Both", bg=ELEVATED, fg=TEXT1, font=self.f_body, relief="flat", padx=15, pady=8, command=lambda: (txt_a.delete("1.0","end"), txt_b.delete("1.0","end"))).pack(side="left", padx=15)

    def _build_history(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        tk.Label(inner, text="📜 Analysis History", bg=BG, fg=TEXT1, font=self.f_title).pack(anchor="w", padx=30, pady=20)
        
        toolbar = tk.Frame(inner, bg=BG, padx=30)
        toolbar.pack(fill="x", pady=(0,10))
        
        tk.Label(toolbar, text="Search:", bg=BG, fg=TEXT2).pack(side="left")
        search_ent = ttk.Entry(toolbar, font=self.f_body, width=20)
        search_ent.pack(side="left", padx=10)
        
        tk.Label(toolbar, text="Filter:", bg=BG, fg=TEXT2).pack(side="left", padx=(10,0))
        filter_var = tk.StringVar(value="All")
        filter_cb = ttk.Combobox(toolbar, textvariable=filter_var, values=["All", "Low", "Medium", "High"], state="readonly", width=10)
        filter_cb.pack(side="left", padx=10)
        
        list_card = self._card(inner)
        list_card.pack(fill="both", expand=True, padx=30, pady=10)
        
        cols = ("ID", "Date", "Preview", "Score", "Level", "Words")
        tree = ttk.Treeview(list_card, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("ID", width=0, stretch=False)
        tree.column("Date", width=120)
        tree.column("Preview", width=400)
        tree.column("Score", width=80)
        tree.column("Level", width=150)
        tree.column("Words", width=80)
        tree.pack(fill="both", expand=True)
        
        self._history_data = []
        
        def load_data():
            tree.delete(*tree.get_children())
            self._history_data = get_user_history(self.user_info["id"])
            q = search_ent.get().lower()
            f = filter_var.get()
            
            for rec in self._history_data:
                ui_level = verdict_to_ui_label(rec["verdict"])
                if f != "All" and ui_level.split()[0] != f:
                    continue
                if q and q not in rec["text_preview"].lower():
                    continue
                tree.insert("", "end", values=(rec["id"], rec["created_at"], rec["text_preview"], rec["score"], ui_level, rec["word_count"]))
                
        def on_double_click(event):
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0])
            rid = item["values"][0]
            rec = next((r for r in self._history_data if r["id"] == rid), None)
            if rec:
                messagebox.showinfo(f"Preview - {rec['created_at']}", rec["text_preview"])

        tree.bind("<Double-1>", on_double_click)
        search_ent.bind("<KeyRelease>", lambda e: load_data())
        filter_cb.bind("<<ComboboxSelected>>", lambda e: load_data())
        
        btn_row = tk.Frame(inner, bg=BG, padx=30)
        btn_row.pack(fill="x", pady=10)
        
        def do_delete():
            sel = tree.selection()
            if not sel: return
            if messagebox.askyesno("Confirm Delete", "Delete selected record?"):
                rid = tree.item(sel[0])["values"][0]
                delete_analysis(self.user_info["id"], rid)
                load_data()
                
        def do_clear():
            if messagebox.askyesno("Confirm Clear", "Clear all history? This cannot be undone."):
                clear_user_history(self.user_info["id"])
                load_data()
                
        def do_export():
            if not self._history_data: return
            fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if fpath:
                try:
                    with open(fpath, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Date", "Preview", "Score", "Verdict", "Words"])
                        for r in self._history_data:
                            writer.writerow([r["created_at"], r["text_preview"], r["score"], verdict_to_ui_label(r["verdict"]), r["word_count"]])
                    messagebox.showinfo("Exported", f"History exported to {fpath}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        
        tk.Button(btn_row, text="🔄 Refresh", bg=ELEVATED, fg=TEXT1, relief="flat", command=load_data).pack(side="left")
        tk.Button(btn_row, text="🗑️ Delete Selected", bg=COLOR_HI, fg="white", relief="flat", command=do_delete).pack(side="left", padx=10)
        tk.Button(btn_row, text="⚠️ Clear All", bg=ELEVATED, fg=COLOR_HI, relief="flat", command=do_clear).pack(side="left")
        tk.Button(btn_row, text="📥 Export CSV", bg=ACCENT, fg="white", relief="flat", command=do_export).pack(side="right")
        
        frame.refresh = load_data

    def _build_settings(self, frame):
        outer, inner = self._scrollable_frame(frame)
        outer.pack(fill="both", expand=True)
        
        tk.Label(inner, text="⚙️ Settings", bg=BG, fg=TEXT1, font=self.f_title).pack(anchor="w", padx=30, pady=20)
        
        prof = self._card(inner)
        prof.pack(fill="x", padx=30, pady=10)
        tk.Label(prof, text="Profile", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0,15))
        
        tk.Label(prof, text="Email Address", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        tk.Label(prof, text=self.user_info["email"], bg=CARD, fg=TEXT1, font=self.f_body).pack(anchor="w", pady=(0,15))
        
        tk.Label(prof, text="Display Name", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        name_ent = ttk.Entry(prof, font=self.f_body)
        name_ent.insert(0, self.user_info["name"])
        name_ent.pack(fill="x", pady=(0,10))
        
        def save_name():
            n = name_ent.get().strip()
            if not n: return
            succ, msg = update_user_name(self.user_info["id"], n)
            if succ:
                self.user_info["name"] = n
                self._user_label.config(text=n)
                messagebox.showinfo("Success", "Name updated successfully.")
            else:
                messagebox.showerror("Error", msg)
                
        tk.Button(prof, text="Update Profile", bg=ACCENT, fg="white", relief="flat", command=save_name).pack(anchor="w")
        
        sec = self._card(inner)
        sec.pack(fill="x", padx=30, pady=20)
        tk.Label(sec, text="Security", bg=CARD, fg=TEXT1, font=self.f_head).pack(anchor="w", pady=(0,15))
        
        tk.Label(sec, text="Current Password", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        p1 = ttk.Entry(sec, show="*", font=self.f_body)
        p1.pack(fill="x", pady=(0,10))
        
        tk.Label(sec, text="New Password", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        p2 = ttk.Entry(sec, show="*", font=self.f_body)
        p2.pack(fill="x", pady=(0,10))
        
        tk.Label(sec, text="Confirm New Password", bg=CARD, fg=TEXT2, font=self.f_small).pack(anchor="w")
        p3 = ttk.Entry(sec, show="*", font=self.f_body)
        p3.pack(fill="x", pady=(0,15))
        
        def save_pwd():
            o, n, c = p1.get(), p2.get(), p3.get()
            if not o or not n or not c:
                messagebox.showwarning("Required", "Fill all password fields.")
                return
            if n != c:
                messagebox.showerror("Error", "New passwords do not match.")
                return
            succ, msg = change_password(self.user_info["id"], o, n)
            if succ:
                messagebox.showinfo("Success", "Password changed successfully.")
                p1.delete(0, "end"); p2.delete(0, "end"); p3.delete(0, "end")
            else:
                messagebox.showerror("Error", msg)
                
        tk.Button(sec, text="Change Password", bg=ACCENT, fg="white", relief="flat", command=save_pwd).pack(anchor="w")
        
        tk.Button(inner, text="Sign Out", bg=ELEVATED, fg=TEXT1, font=self.f_body, relief="flat", padx=20, pady=10, command=self._logout).pack(anchor="w", padx=30, pady=20)

    def _logout(self):
        self.user_info = None
        self._main.destroy()
        self.pages = {}
        self._current_page = None
        self._show_login_state()

if __name__ == '__main__':
    app = FakeNewsApp()
    app.mainloop()