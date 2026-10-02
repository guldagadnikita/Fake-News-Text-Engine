import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    src = f.read()

# Extract page_home code
home_match = re.search(r'def page_home\(\):(.*?)(?=\ndef \w)', src, re.DOTALL)
home_code = home_match.group(1) if home_match else ''

# Extract page_assistant code
asst_match = re.search(r'def page_assistant\(\):(.*?)(?=\ndef \w|\n# ===)', src, re.DOTALL)
asst_code = asst_match.group(1) if asst_match else ''

results = [
    ('Home has NO chat_input',       'chat_input' not in home_code),
    ('Home has NO chat_message',     'chat_message' not in home_code),
    ('Home has NO _bot_reply',       '_bot_reply' not in home_code),
    ('Home has Hero',                'RULE-BASED TEXT ANALYSIS ENGINE' in home_code),
    ('Home has Try Example',         'Try an Example' in home_code),
    ('Home has Score Guide',         'Score Guide' in home_code),
    ('Home has Engine Rules',        'What the Engine Checks' in home_code),
    ('Home has Disclaimer',          'Important' in home_code),
    ('Home has NO How It Works',     'How It Works' not in home_code),
    ('Assistant has chat_input',     'chat_input' in asst_code),
    ('Assistant has chat_message',   'chat_message' in asst_code),
    ('Assistant has _bot_reply',     '_bot_reply' in asst_code),
    ('Assistant has Clear Chat',     'Clear Chat' in asst_code),
    ('Router has page_assistant()',  'page_assistant()' in src),
    ('Sidebar has Engine Assistant', 'Engine Assistant' in src),
    ('_bot_reply function exists',   'def _bot_reply(' in src),
    ('assistant_messages in state',  'assistant_messages' in src),
    ('Bot handles score',           'score calculated' in src or 'score calculation' in src),
    ('Bot handles rules',           'detection rules' in src),
    ('Bot handles latest result',   'latest result' in src),
    ('Bot handles readability',     'readability' in src),
    ('Bot handles sentiment',       'sentiment' in src),
    ('Bot handles comparison',      'compare' in src),
    ('Bot handles reports',         'report' in src),
    ('Bot handles history',         'history' in src),
    ('Bot handles technology',      'technology' in src),
    ('Bot handles unknown',         "I'm not sure" in src or "I can help with" in src),
    ('Bot handles tokenization',    'token' in src),
]

print('=== VERIFICATION ===')
all_ok = True
for label, passed in results:
    status = 'OK' if passed else 'FAIL'
    if not passed: all_ok = False
    print(f'  [{status}] {label}')

# Check nav order
nav_block = src[src.find('nav_items = ['):src.find('nav_items = [') + 800]
comp_pos = nav_block.find('Comparison')
asst_pos = nav_block.find('Engine Assistant')
hist_pos = nav_block.find('History')
correct = comp_pos < asst_pos < hist_pos
print(f'  [{"OK" if correct else "FAIL"}] Nav order: Comparison({comp_pos}) < Assistant({asst_pos}) < History({hist_pos})')
if not correct: all_ok = False

lines = src.count('\n') + 1
print(f'\nTotal lines: {lines}')
print(f'RESULT: {"ALL PASSED" if all_ok else "SOME FAILED"}')
