"""Command line: ``uv run --group evals python -m evals run --model <id>``."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="evals", description="Score how well a model handles Brazilian Portuguese.")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="test one model")
    run.add_argument("--model", required=True, help="model id from backend/config.py")
    run.add_argument("--judge", default="claude-opus-5-5", help="Claude model that grades the answers")
    commands.add_parser("leaderboard", help="print the table of tested models")
    parser.parse_args()
    raise NotImplementedError("The tester isn't implemented yet")


if __name__ == "__main__":
    main()
