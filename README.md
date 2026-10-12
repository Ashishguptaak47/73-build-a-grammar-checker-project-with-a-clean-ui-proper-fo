# ScribeGuard - Grammar & Writing Checker

A modern, responsive, extensible Python grammar, style, and readability checking application. Built with a modular Python rule engine and an interactive real-time Flask Web UI.

## Features

- **Comprehensive Checks**:
  - **Grammar & Agreement**: Subject-verb mismatches (`he don't` $\rightarrow$ `he doesn't`, `I is` $\rightarrow$ `I am`, modal verbs `could of` $\rightarrow$ `could have`).
  - **Duplicated Words**: Identifies consecutive duplicated words like `the the`.
  - **Spelling & Homophones**: Catches frequently confused words (`their/they're`, `your/you're`, `then/than`, `loose/lose`, `its/it's`).
  - **Wordiness & Style**: Identifies verbose phrases (`in order to` $\rightarrow$ `to`, `due to the fact that` $\rightarrow$ `because`).
  - **Typography & Punctuation**: Spacing before/after punctuation marks, sentence start capitalization, standalone `i` pronoun capitalization.
- **Readability Scoring**:
  - Automated Flesch Reading Ease and Flesch-Kincaid Grade Level.
  - Live audience difficulty rating and word/character counters.
- **Interactive UI**:
  - Side-by-side backdrop overlay highlighting issues.
  - Category filter dropdown.
  - Instant one-click individual fixes or "Auto-Fix All".
- **CLI Mode**: Run grammar checks from terminal without opening a browser.

## Project Structure

```
.
├── grammar_checker/
│   ├── __init__.py
│   ├── models.py       # Data structures (Issue, Metrics, Categories)
│   ├── rules.py        # Grammar and style rules definitions
│   └── engine.py       # Core analysis and text rewriting engine
├── templates/
│   └── index.html      # Responsive HTML5 interface
├── static/
│   ├── style.css       # Clean modern dark theme
│   └── app.js          # Interactive frontend & async check loop
├── tests/
│   └── test_main.py    # Unit & integration tests
├── main.py             # Flask application & CLI entrypoint
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Web Application

```bash
python main.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

### 3. Run in CLI Mode

```bash
python main.py --cli "he don't understand the the problem. in order to fix this, i will help."
```

### 4. Run Tests

```bash
pytest
```
