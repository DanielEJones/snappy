from typing import Callable
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree
from pathlib import Path

from snappy.suite import TestSuite
from snappy.test import Test


def arg_capturer(context: list) -> Callable:
    def capture_args(*args, **kwargs):
        context.append([args, kwargs])
    return capture_args


class TestNewSuite(TestCase):

    def setUp(self) -> None:
        self.suite = TestSuite("./snaps")
        self.context = []

        @self.suite.test_case
        def my_test_case(test: Test) -> None:
            self.context.append("my_test_case")
            _ = test

        @self.suite.test_case
        def second_case(test: Test) -> None:
            self.context.append("second_case")
            _ = test

        _, _ = my_test_case, second_case


    def test_adds_cases(self) -> None:
        self.assertEqual(2, len(self.suite._tests))

    def test_runs_tests(self) -> None:
        # Set the display func to discard the output during tests
        self.suite.run_tests()
        self.assertEqual(["my_test_case", "second_case"], self.context)


# class TestReporting(TestCase):
#
#     def get_snapped_value(self) -> str:
#         return self.snapped_value
#
#     def setUp(self) -> None:
#         self.snap_path = Path(mkdtemp())
#         self.suite = TestSuite(self.snap_path)
#
#         self.snapped_value = "hello, world!"
#
#         @self.suite.test_case
#         def test_something(test: Test) -> None:
#             test.snap(self.get_snapped_value(), "snap1")
#
#         _ = test_something
#
#     def test_first_snaps(self) -> None:
#         capture = []
#         self.suite.run_tests(display_func=arg_capturer(capture))
#         self.assertEqual(
#             [[('test_something:',), {'end': ' \t'}], [('err!',), {}],
#              [('  x snap1',), {}],
#              [('-----------------------------------',), {}],
#              [('1 test ran:',), {}],
#              [('  0 tests passed',), {}],
#              [('  1 test failed',), {}],
#              [('  1 new snap to review',), {}]],
#             capture
#         )
#
#     def test_two_same_snaps(self) -> None:
#         self.suite.run_tests(display_func=arg_capturer([]))
#
#         # Strip new suffix
#         for file in self.snap_path.rglob("*.new"):
#             file.rename(file.with_suffix(""))
#
#         capture = []
#         self.suite.run_tests(display_func=arg_capturer(capture))
#         self.assertEqual(
#             [[('test_something:',), {'end': ' \t'}], [('ok.',), {}],
#              [('-----------------------------------',), {}],
#              [('1 test ran:',), {}],
#              [('  1 test passed',), {}],
#              [('  0 tests failed',), {}],
#              [('  0 new snaps to review',), {}]],
#             capture
#         )
#
#     def test_two_different_snaps(self) -> None:
#         self.suite.run_tests(display_func=arg_capturer([]))
#
#         # Strip new suffix
#         for file in self.snap_path.rglob("*.new"):
#             file.rename(file.with_suffix(""))
#
#         self.snapped_value = "goodbye, moon!"
#
#         capture = []
#         self.suite.run_tests(display_func=arg_capturer(capture))
#         self.assertEqual(
#             [[('test_something:',), {'end': ' \t'}], [('err!',), {}],
#              [('  x snap1',), {}],
#              [('-----------------------------------',), {}],
#              [('1 test ran:',), {}],
#              [('  0 tests passed',), {}],
#              [('  1 test failed',), {}],
#              [('  1 new snap to review',), {}]],
#             capture
#         )
#
#     def tearDown(self) -> None:
#         rmtree(self.snap_path)

