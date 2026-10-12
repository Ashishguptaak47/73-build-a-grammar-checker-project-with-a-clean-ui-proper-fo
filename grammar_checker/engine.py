import re
import math
from typing import List, Tuple
from .models import Issue, CheckResult, ReadabilityMetrics
from .rules import RULES, Rule


class GrammarEngine:
    def __init__(self, rules: List[Rule] = None):
        self.rules = rules if rules is not None else RULES

    def analyze(self, text: str) -> CheckResult:
        if not text or not text.strip():
            empty_metrics = ReadabilityMetrics(
                word_count=0,
                sentence_count=0,
                character_count=0,
                syllable_count=0,
                flesch_reading_ease=100.0,
                flesch_kincaid_grade=0.0,
                reading_level="N/A"
            )
            return CheckResult(text=text, issues=[], metrics=empty_metrics)

        issues = self._find_issues(text)
        metrics = self._calculate_metrics(text)
        return CheckResult(text=text, issues=issues, metrics=metrics)

    def _find_issues(self, text: str) -> List[Issue]:
        detected: List[Issue] = []
        for rule in self.rules:
            detected.extend(rule.find_issues(text))

        # Sentence boundary capitalization check
        sentence_cap_issues = self._check_sentence_capitalization(text)
        detected.extend(sentence_cap_issues)

        # Sort issues strictly by character offset and length
        detected.sort(key=lambda x: (x.start, -x.end))

        # Filter overlapping issues to preserve clean replacements
        filtered: List[Issue] = []
        last_end = -1
        for issue in detected:
            if issue.start >= last_end:
                filtered.append(issue)
                last_end = issue.end
        return filtered

    def _check_sentence_capitalization(self, text: str) -> List[Issue]:
        from .models import Category, Severity
        issues = []
        # Match sentence boundaries (start of text or after terminal punctuation followed by space)
        pattern = re.compile(r"(^|[.!?]\s+)([a-z])")
        for m in pattern.finditer(text):
            char_span_start = m.start(2)
            char_span_end = m.end(2)
            lower_char = m.group(2)
            issues.append(Issue(
                id=f"sent_cap_{char_span_start}",
                category=Category.STYLE,
                severity=Severity.WARNING,
                start=char_span_start,
                end=char_span_end,
                matched_text=lower_char,
                message="Sentence should start with a capitalized letter",
                replacements=[lower_char.upper()],
                explanation="Capitalize the first letter of every new sentence."
            ))
        return issues

    def _calculate_metrics(self, text: str) -> ReadabilityMetrics:
        char_count = len(text)
        words = re.findall(r"\b[a-zA-Z0-9']+\b", text)
        word_count = len(words)

        sentences = re.split(r"[.!?]+\s*", text.strip())
        sentence_count = len([s for s in sentences if s.strip()])
        sentence_count = max(1, sentence_count)

        total_syllables = sum(self._count_syllables(w) for w in words)
        total_syllables = max(word_count, total_syllables)

        if word_count == 0:
            return ReadabilityMetrics(0, 0, char_count, 0, 100.0, 0.0, "N/A")

        words_per_sentence = word_count / sentence_count
        syllables_per_word = total_syllables / word_count

        # Flesch Reading Ease Formula: 206.835 - (1.015 * ASL) - (84.6 * ASW)
        fre = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        fre = max(0.0, min(100.0, round(fre, 1)))

        # Flesch-Kincaid Grade Level: (0.39 * ASL) + (11.8 * ASW) - 15.59
        fkgl = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59
        fkgl = max(0.0, round(fkgl, 1))

        if fre >= 90:
            level = "Very Easy (5th grade)"
        elif fre >= 80:
            level = "Easy (6th grade)"
        elif fre >= 70:
            level = "Fairly Easy (7th grade)"
        elif fre >= 60:
            level = "Standard (8th-9th grade)"
        elif fre >= 50:
            level = "Fairly Difficult (10th-12th)"
        elif fre >= 30:
            level = "Difficult (College)"
        else:
            level = "Very Difficult (Professional)"

        return ReadabilityMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            character_count=char_count,
            syllable_count=total_syllables,
            flesch_reading_ease=fre,
            flesch_kincaid_grade=fkgl,
            reading_level=level
        )

    @staticmethod
    def _count_syllables(word: str) -> int:
        word = word.lower().strip()
        if not word:
            return 0
        if len(word) <= 3:
            return 1
        word = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", word)
        word = re.sub(r"^y", "", word)
        matches = re.findall(r"[aeiouy]{1,2}", word)
        return max(1, len(matches))

    def apply_replacement(self, text: str, issue_id: str, replacement: str) -> str:
        issues = self._find_issues(text)
        for issue in issues:
            if issue.id == issue_id:
                return text[:issue.start] + replacement + text[issue.end:]
        return text

    def apply_all_replacements(self, text: str) -> str:
        issues = self._find_issues(text)
        # Apply fixes backwards to avoid offset desynchronization
        for issue in reversed(issues):
            if issue.replacements:
                best_replacement = issue.replacements[0]
                text = text[:issue.start] + best_replacement + text[issue.end:]
        return text
