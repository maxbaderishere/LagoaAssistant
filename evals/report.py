"""Scores, saved results and the model leaderboard."""

from dataclasses import dataclass
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class TaskResult:
    """What happened with one task: the answer, the checks and the judge's grade."""
    task_id: str
    category: str
    answer: str | None
    score: float | None  # 0-100; None if the model failed to answer
    error: str | None = None


@dataclass
class Report:
    """All results of one run of the tester on one model."""
    model: str
    judge: str
    results: list[TaskResult]

    def category_scores(self) -> dict[str, float]:
        """Mean score of each category."""
        raise NotImplementedError

    def overall_score(self) -> float:
        """The model's score from 0 to 100: the mean of the category scores.

        Averaging categories rather than tasks keeps a category with many
        tasks from outweighing the others.
        """
        raise NotImplementedError

    def save(self) -> Path:
        """Write the report to ``evals/results/<date>_<model>.json``."""
        raise NotImplementedError


def leaderboard() -> str:
    """A Markdown table of the latest score of every tested model."""
    raise NotImplementedError
