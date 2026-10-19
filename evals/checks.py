"""Cheap automatic checks that run before the judge and cost nothing.

A task lists the checks it needs by name in its ``checks`` field, e.g.
``language_pt`` or ``max_words: 50``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one automatic check."""
    name: str
    passed: bool
    detail: str = ""
    fatal: bool = False  # a fatal failure (e.g. the answer isn't Portuguese) scores the task 0


def run_checks(answer: str, checks: list[str | dict]) -> list[CheckResult]:
    """Run a task's automatic checks on an answer.

    Planned checks:
        language_pt: the answer is in Portuguese, not Spanish or English (fatal).
        no_pt_pt: no European Portuguese markers (telemóvel, autocarro, "estar a fazer", tu forms).
        max_words: N: the answer has at most N words.
        bullet_count: N: the answer is a list of exactly N items.
        max_bullets: N: the answer is a list of at most N items.
        line_count: N: the answer has exactly N non-empty lines (e.g. a haiku).
        json_only: the answer is valid JSON and nothing else, without a Markdown fence.
    """
    raise NotImplementedError
