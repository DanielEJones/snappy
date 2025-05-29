from unittest import TestCase

from snappy.suite import TestSuite
from snappy.test import Test


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
        self.suite.run_tests()
        self.assertEqual(["my_test_case", "second_case"], self.context)

