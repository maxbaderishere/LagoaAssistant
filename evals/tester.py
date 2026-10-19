"""The tester: runs the tasks on a model and collects graded results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from backend.ai import Client

if TYPE_CHECKING:
    from evals.judge import Judge
    from evals.report import Report

TASKS_DIR = Path(__file__).parent / "tasks"

CATEGORIES = {
    "grammar": "Грамматика и естественность",
    "pt_br": "pt-BR, а не pt-PT",
    "br_context": "Бразильский контекст",
    "instructions": "Следование инструкциям",
    "register": "Регистр: формально или неформально",
    "colloquial": "Понимание разговорного языка",
    "summarization": "Пересказ и суммаризация",
}


@dataclass(frozen=True)
class Task:
    """One prompt for the model under test, with what a good answer must do.

    Attributes:
        id: Unique id, e.g. ``ctx-001``.
        category: One of ``CATEGORIES``.
        prompt: What the model is asked, in pt-BR.
        criteria: What the judge checks; each criterion is scored 0-10.
        checks: Automatic checks from ``evals.checks`` to run first.
        reference: An example of a good answer, if one helps the judge.
    """
    id: str
    category: str
    prompt: str
    criteria: list[str]
    checks: list[str | dict] = field(default_factory=list)
    reference: str | None = None


def load_tasks(path: Path = TASKS_DIR / "pt_br.yaml") -> list[Task]:
    """Load tasks from a YAML file."""
    import yaml

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Task(**item) for item in raw["tasks"]]


class PortugueseTester:
    """Runs every task on the model under test and has the judge grade each answer."""

    def __init__(self, subject: Client, judge: Judge, tasks: list[Task]):
        self._subject = subject
        self._judge = judge
        self._tasks = tasks

    def run(self) -> Report:
        """Ask the model every task, run the automatic checks, then the judge.

        A failed request (rate limit, timeout) is recorded as an error rather
        than scored 0, so outages don't look like bad Portuguese.
        """
        raise NotImplementedError
