"""Helper tasks: work done for the app by a model, not answers to the user.

Each helper receives a ``Client`` and doesn't care which model it is, so the
same task can run on a small local model or on the chat's own model.
"""

from backend.helpers.replies import ReplySuggester
from backend.helpers.summaries import Summariser
from backend.helpers.titles import TitleWriter

__all__ = ["ReplySuggester", "Summariser", "TitleWriter"]
