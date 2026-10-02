import sys, ast
sys.path.insert(0, '.')

with open('tkinter_app.py', 'r', encoding='utf-8') as f:
    src = f.read()

tree = ast.parse(src)
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
print('Classes:', classes)
print('Total functions:', len(funcs))

key_funcs = [
    'verdict_to_ui_label', 'verdict_to_color',
    '_show_login_state', '_show_main_state', '_build_sidebar', '_show_page',
    '_metric_card', '_run_detection', '_detection_worker',
    '_display_detection_results', '_build_detection', '_build_dashboard',
    '_build_history', '_build_settings', '_logout',
    '_handle_login', '_handle_register'
]
all_ok = True
for fn in key_funcs:
    found = fn in funcs
    if not found:
        all_ok = False
    print(f"  [{'OK' if found else 'MISSING'}] {fn}")

print()
if all_ok:
    print("Tkinter structure check: ALL KEY METHODS PRESENT")
else:
    print("Tkinter structure check: SOME METHODS MISSING")

# Check key content
content_checks = [
    ('News Credibility Checker', 'page heading'),
    ('threading.Thread', 'background thread'),
    ('self.after(0', 'thread-safe UI'),
    ('FigureCanvasTkAgg', 'matplotlib chart'),
    ('ttk.Treeview', 'history treeview'),
    ('verdict_to_ui_label', 'label mapping'),
    ('Score Breakdown', 'breakdown section'),
    ('6366F1', 'indigo accent'),
    ('0B0F19', 'bg color'),
    ('151C2C', 'card color'),
    ('MEDIUM SUSPICION', 'medium level label'),
]
print()
print("Content checks:")
for term, label in content_checks:
    found = term in src
    print(f"  [{'OK' if found else 'MISSING'}] {label}")
