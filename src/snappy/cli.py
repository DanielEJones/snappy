from argparse import ArgumentParser
from pathlib import Path

from .core import run_tests, review_snaps


def main() -> None:
    parser = ArgumentParser(description="A snapshot test manager.")
    mode = parser.add_subparsers(dest="mode", required=True, help="Must select a mode of operation")

    # Test mode, to discover and execute tests
    test = mode.add_parser("test", help="Select a directory to discover tests.")
    test.add_argument("directory", type=Path, help="Path to test directory.")

    # Review mode, to discover and review snapshots
    review = mode.add_parser("review", help="Select a directory to review.")
    review.add_argument("directory", type=Path, help="Path to review.")

    match (args := parser.parse_args()).mode:
        case "test":   run_tests(args.directory)
        case "review": review_snaps(args.directory)

