"""Judges: models that grade an answer against a task's criteria."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from evals.tester import Task


@dataclass(frozen=True)
class CriterionScore:
    """How well the answer meets one criterion of the task."""
    criterion: str
    score: int  # 0-10, using the anchors in the judge's rubric
    reason: str


@dataclass(frozen=True)
class Grade:
    """The judge's verdict on one answer."""
    criteria: list[CriterionScore]
    comment: str

    @property
    def score(self) -> float:
        """The answer's score from 0 to 100: the mean of the criteria scores."""
        return sum(c.score for c in self.criteria) / len(self.criteria) * 10 if self.criteria else 0.0


class Judge(ABC):
    """Grades answers. Separate from ``Client``: a judge must return scores, not free text."""

    @abstractmethod
    def grade(self, task: Task, answer: str) -> Grade:
        """Grade an answer to a task. The judge never learns which model wrote it."""


class ClaudeJudge(Judge):
    """Judge backed by Claude, returning validated structured output."""

    def __init__(self, api_key: str, model: str = "claude-opus-5-5", effort: str = "high"):
        self._api_key = api_key
        self._model = model
        self._effort = effort

    def grade(self, task: Task, answer: str) -> Grade:
        raise NotImplementedError
