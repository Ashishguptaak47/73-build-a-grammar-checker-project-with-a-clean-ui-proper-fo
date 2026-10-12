from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional


class Category(str, Enum):
    GRAMMAR = "grammar"
    SPELLING = "spelling"
    STYLE = "style"
    PUNCTUATION = "punctuation"
    WORDINESS = "wordiness"


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    id: str
    category: Category
    severity: Severity
    start: int
    end: int
    matched_text: str
    message: str
    replacements: List[str] = field(default_factory=list)
    explanation: Optional[str] = None

    def to_dict(self):
        d = asdict(self)
        d["category"] = self.category.value
        d["severity"] = self.severity.value
        return d


@dataclass
class ReadabilityMetrics:
    word_count: int
    sentence_count: int
    character_count: int
    syllable_count: int
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    reading_level: str

    def to_dict(self):
        return asdict(self)


@dataclass
class CheckResult:
    text: str
    issues: List[Issue]
    metrics: ReadabilityMetrics

    def to_dict(self):
        return {
            "text": self.text,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics.to_dict(),
            "issue_count": len(self.issues)
        }
