from typing import Callable, List
from pathlib import Path

from .test import Test
from .report import Report


class TestSuite:
    """
    TestSuites are a logical collection of tests. The suite objects will be discovered by the test
    runner, which will then execute all tests associated with the suite and report the results.
    """

    def __init__(self, snapshot_directory: str | Path) -> None:
        """
        Creates a new test suite.

        Args:
            snapshot_directory: the path you would like snapshots to be stored in.
        """
        if not isinstance(snapshot_directory, Path):
            snapshot_directory = Path(snapshot_directory)

        self._snaps_dir = snapshot_directory
        if not self._snaps_dir.exists():
            self._snaps_dir.mkdir(parents=True, exist_ok=True)

        self._tests: List[Test] = []


    def test_case(self, test: Callable[[Test], None]) -> Callable[[Test], None]:
        """
        Decotator that marks a function as a test and registers it with the suite.

        Args:
            test: the function containing test logic.
        """
        self._tests.append(Test(
            name = test.__name__,
            function = test,
            snap_directory = self._snaps_dir
        ))

        # Return the function as is, now that we've registered it.
        return test


    def run_tests(self) -> None:
        """
        Executes all tests registered with the suite.

        Args:
            display_func: The callable that results will be pushed to.
        """

        report = Report("suite")

        for test in self._tests:
            test_report = report.get_child_by_path(test._name)
            test._run(test_report)

