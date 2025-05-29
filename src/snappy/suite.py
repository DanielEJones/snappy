from typing import Callable, List
from pathlib import Path

from .test import Test


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


    def run_tests(self, display_func: Callable = print) -> None:
        """
        Executes all tests registered with the suite.

        Args:
            display_func: The callable that results will be pushed to.
        """
        snaps_for_review = 0
        tests_failed = 0
        for test in self._tests:
            display_func(f"{test._name}:", end=" \t")

            if test._run():
                display_func("ok.")

            else:
                tests_failed = tests_failed + 1
                snaps_for_review = snaps_for_review + len(test._new_snaps)
                display_func('err!')
                display_func('\n'.join([
                    f"  x {snap}" for snap in test._new_snaps
                ]))

        n_tests = len(self._tests)
        tests_passed = n_tests - tests_failed

        def plural(n: int, word: str) -> str:
            return f"1 {word}" if n == 1 else f"{n} {word}s"

        display_func("-----------------------------------")
        display_func(f"{plural(n_tests, 'test')} ran:")
        display_func(f"  {plural(tests_passed, 'test')} passed")
        display_func(f"  {plural(tests_failed, 'test')} failed")
        display_func(f"  {plural(snaps_for_review, 'new snap')} to review")

