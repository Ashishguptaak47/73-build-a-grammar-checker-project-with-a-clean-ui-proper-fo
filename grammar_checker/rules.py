import re
from typing import List, Tuple, Callable, Optional
from .models import Issue, Category, Severity


class Rule:
    def __init__(
        self,
        rule_id: str,
        pattern: str,
        category: Category,
        severity: Severity,
        message_template: str,
        replacements_builder: Callable[[re.Match], List[str]],
        explanation: str = "",
        flags: int = re.IGNORECASE
    ):
        self.rule_id = rule_id
        self.pattern = re.compile(pattern, flags)
        self.category = category
        self.severity = severity
        self.message_template = message_template
        self.replacements_builder = replacements_builder
        self.explanation = explanation

    def find_issues(self, text: str) -> List[Issue]:
        issues = []
        for match in self.pattern.finditer(text):
            start, end = match.span()
            matched_text = match.group(0)
            replacements = self.replacements_builder(match)
            msg = self.message_template.format(*match.groups())
            issues.append(Issue(
                id=f"{self.rule_id}_{start}",
                category=self.category,
                severity=self.severity,
                start=start,
                end=end,
                matched_text=matched_text,
                message=msg,
                replacements=replacements,
                explanation=self.explanation
            ))
        return issues


# Dynamic capitalization handler
def _cap_first(word: str) -> str:
    return word[:1].upper() + word[1:] if word else ""


RULES: List[Rule] = [
    # 1. Repeated consecutive words (e.g. "the the")
    Rule(
        rule_id="repeated_words",
        pattern=r"\b(\w+)\s+\1\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Duplicated word detected: '{}'",
        replacements_builder=lambda m: [m.group(1)],
        explanation="Avoid accidentally typing the same word twice consecutively."
    ),

    # 2. "could of", "should of", "would of"
    Rule(
        rule_id="modal_of",
        pattern=r"\b(could|should|would|might|must)\s+of\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Did you mean '{} have'?",
        replacements_builder=lambda m: [f"{m.group(1)} have"],
        explanation="Use the auxiliary verb 'have' rather than preposition 'of'."
    ),

    # 3. Subject-Verb agreement: He/She/It don't
    Rule(
        rule_id="sva_dont",
        pattern=r"\b(he|she|it|this|that)\s+don't\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Third-person singular pronoun with 'don't'",
        replacements_builder=lambda m: [f"{m.group(1)} doesn't"],
        explanation="Third-person singular subjects take 'doesn't' instead of 'don't'."
    ),

    # 4. Subject-Verb agreement: They/We/You doesn't
    Rule(
        rule_id="sva_doesnt",
        pattern=r"\b(they|we|you)\s+doesn't\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Plural/second-person pronoun with 'doesn't'",
        replacements_builder=lambda m: [f"{m.group(1)} don't"],
        explanation="Plural subjects and 'you' require 'don't' in negative present tense."
    ),

    # 5. Subject-Verb agreement: I is / He are / They is
    Rule(
        rule_id="sva_be_i",
        pattern=r"\bI\s+is\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Subject-verb mismatch for 'I'",
        replacements_builder=lambda m: ["I am"],
        explanation="Use 'I am' rather than 'I is'."
    ),
    Rule(
        rule_id="sva_be_he_she",
        pattern=r"\b(he|she|it)\s+are\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Third person singular requires 'is'",
        replacements_builder=lambda m: [f"{m.group(1)} is"],
        explanation="Third-person singular pronouns take 'is'."
    ),
    Rule(
        rule_id="sva_be_they",
        pattern=r"\b(they|we)\s+is\b",
        category=Category.GRAMMAR,
        severity=Severity.CRITICAL,
        message_template="Plural pronoun requires 'are'",
        replacements_builder=lambda m: [f"{m.group(1)} are"],
        explanation="Plural pronouns require 'are'."
    ),

    # 6. Common homophones: their / there / they're
    Rule(
        rule_id="their_going",
        pattern=r"\btheir\s+(going|doing|coming|making|taking|having)\b",
        category=Category.SPELLING,
        severity=Severity.WARNING,
        message_template="Possible confusion with 'they're'",
        replacements_builder=lambda m: [f"they're {m.group(1)}"],
        explanation="Use contraction 'they're' (they are) before present participle verbs."
    ),
    Rule(
        rule_id="your_welcome",
        pattern=r"\byour\s+(welcome|right|wrong|mistaken|correct)\b",
        category=Category.SPELLING,
        severity=Severity.WARNING,
        message_template="Did you mean 'you're {}'?",
        replacements_builder=lambda m: [f"you're {m.group(1)}"],
        explanation="Use 'you're' as the contraction of 'you are'."
    ),
    Rule(
        rule_id="its_an",
        pattern=r"\bits\s+(a|an|the|my|your|very|not|quite)\b",
        category=Category.SPELLING,
        severity=Severity.WARNING,
        message_template="Possible confusion with contraction 'it's'",
        replacements_builder=lambda m: [f"it's {m.group(1)}"],
        explanation="'It's' stands for 'it is', whereas 'its' is the possessive determiner."
    ),
    Rule(
        rule_id="then_than",
        pattern=r"\b(more|less|better|worse|bigger|smaller|faster|slower|higher|lower)\s+then\b",
        category=Category.SPELLING,
        severity=Severity.WARNING,
        message_template="Comparisons use 'than', not 'then'",
        replacements_builder=lambda m: [f"{m.group(1)} than"],
        explanation="'Than' indicates comparison; 'then' denotes time or consequence."
    ),
    Rule(
        rule_id="loose_lose",
        pattern=r"\b(will|to|can|could|might|must)\s+loose\b",
        category=Category.SPELLING,
        severity=Severity.WARNING,
        message_template="Did you mean 'lose' (verb)?",
        replacements_builder=lambda m: [f"{m.group(1)} lose"],
        explanation="'Lose' is a verb meaning to misplace or suffer loss; 'loose' means not tight."
    ),

    # 7. Wordiness & Redundancies
    Rule(
        rule_id="wordy_in_order_to",
        pattern=r"\bin order to\b",
        category=Category.WORDINESS,
        severity=Severity.INFO,
        message_template="Consider conciseness: replace with 'to'",
        replacements_builder=lambda m: ["to"],
        explanation="'In order to' can almost always be simplified to 'to'."
    ),
    Rule(
        rule_id="wordy_at_this_point",
        pattern=r"\bat this point in time\b",
        category=Category.WORDINESS,
        severity=Severity.INFO,
        message_template="Consider replacing with 'now' or 'currently'",
        replacements_builder=lambda m: ["now", "currently"],
        explanation="Verbose phrasing can be replaced with direct adverbs."
    ),
    Rule(
        rule_id="wordy_due_to_fact",
        pattern=r"\bdue to the fact that\b",
        category=Category.WORDINESS,
        severity=Severity.INFO,
        message_template="Replace wordy clause with 'because'",
        replacements_builder=lambda m: ["because", "since"],
        explanation="'Due to the fact that' clutters sentence structure."
    ),
    Rule(
        rule_id="wordy_basic_essentials",
        pattern=r"\bbasic essentials\b",
        category=Category.WORDINESS,
        severity=Severity.INFO,
        message_template="Redundant modifier: 'essentials' is already basic",
        replacements_builder=lambda m: ["essentials"],
        explanation="Avoid tautological phrases."
    ),

    # 8. Punctuation & Spacing
    Rule(
        rule_id="space_before_punct",
        pattern=r"\s+([,.;:?!])",
        category=Category.PUNCTUATION,
        severity=Severity.WARNING,
        message_template="Unwanted whitespace before punctuation mark '{}'",
        replacements_builder=lambda m: [m.group(1)],
        explanation="Punctuation marks should attach directly to the preceding word."
    ),
    Rule(
        rule_id="double_space",
        pattern=r"[ ]{2,}",
        category=Category.PUNCTUATION,
        severity=Severity.INFO,
        message_template="Multiple consecutive spaces found",
        replacements_builder=lambda m: [" "],
        explanation="Use single spacing between words in modern typography."
    ),
    Rule(
        rule_id="missing_comma_space",
        pattern=r",([A-Za-z])",
        category=Category.PUNCTUATION,
        severity=Severity.WARNING,
        message_template="Missing space after comma",
        replacements_builder=lambda m: [f", {m.group(1)}"],
        explanation="Commas should be followed by a space."
    ),

    # 9. Style: Standalone lowercase pronoun 'i'
    Rule(
        rule_id="lowercase_i",
        pattern=r"(?<=\s|^)i(?=[\s.,!?;']|$)",
        category=Category.STYLE,
        severity=Severity.CRITICAL,
        message_template="The pronoun 'I' must always be capitalized",
        replacements_builder=lambda m: ["I"],
        explanation="Personal pronoun 'I' is always capitalized in English.",
        flags=0
    )
]
