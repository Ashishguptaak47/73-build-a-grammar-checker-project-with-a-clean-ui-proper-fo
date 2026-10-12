import os
import sys
import argparse
from flask import Flask, request, jsonify, render_template
from grammar_checker.engine import GrammarEngine

app = Flask(__name__, template_folder="templates", static_folder="static")
engine = GrammarEngine()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json() or {}
    text = data.get("text", "")
    result = engine.analyze(text)
    return jsonify(result.to_dict())


@app.route("/api/fix", methods=["POST"])
def api_fix():
    data = request.get_json() or {}
    text = data.get("text", "")
    issue_id = data.get("issue_id", "")
    replacement = data.get("replacement", "")
    fixed_text = engine.apply_replacement(text, issue_id, replacement)
    return jsonify({"fixed_text": fixed_text})


@app.route("/api/fix-all", methods=["POST"])
def api_fix_all():
    data = request.get_json() or {}
    text = data.get("text", "")
    fixed_text = engine.apply_all_replacements(text)
    return jsonify({"fixed_text": fixed_text})


def run_cli(input_text: str):
    res = engine.analyze(input_text)
    print(f"\n--- ScribeGuard Analysis ---")
    print(f"Readability Score : {res.metrics.flesch_reading_ease} ({res.metrics.reading_level})")
    print(f"Grade Level       : {res.metrics.flesch_kincaid_grade}")
    print(f"Word Count        : {res.metrics.word_count}")
    print(f"Issues Found      : {len(res.issues)}\n")
    for idx, iss in enumerate(res.issues, 1):
        print(f"{idx}. [{iss.category.upper()}] '{iss.matched_text}' -> {iss.message}")
        if iss.replacements:
            print(f"   Suggestions: {', '.join(iss.replacements)}")
    print("\n--- Auto-Corrected Version ---")
    print(engine.apply_all_replacements(input_text))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScribeGuard Grammar Checker")
    parser.add_argument("--cli", type=str, help="Run in CLI mode with the provided input text")
    parser.add_argument("--port", type=int, default=5000, help="Port to run web app")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run web app")
    args = parser.parse_args()

    if args.cli:
        run_cli(args.cli)
    else:
        port = int(os.environ.get("PORT", args.port))
        print(f"Starting ScribeGuard Grammar Checker on http://{args.host}:{port}")
        app.run(host=args.host, port=port, debug=True)
