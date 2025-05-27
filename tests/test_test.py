from typing import Callable
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree
from pathlib import Path

from snappy.snapshot import Snapshot
from snappy.test import Test


def tester(test: Test) -> None:
    ...

class TestFileHandling(TestCase):

    def setUp(self) -> None:
        self.path = Path(mkdtemp())

    def test_makes_new_directory(self) -> None:
        Test("test", tester, self.path / "tests" / "snaps")
        self.assertTrue((self.path / "tests" / "snaps").exists())

    def test_makes_new_snaps_first_time(self) -> None:
        test = Test("test_makes_snaps", tester, self.path)
        test.snap("hello, world!\n", "test_snap")
        test.snap("this is a test!", "second_snap")
        self.assertEqual(['test_snap', 'second_snap'], test._new_snaps)

    def test_makes_new_snap_existing_but_different(self) -> None:
        test = Test("test_snap", tester, self.path)
        snap = Snapshot.new("test_snap", "snap", "this is content")
        snap.save_to(self.path / "test_snap" / f"snap.snap")
        test.snap("this is not content", "snap")
        self.assertEqual(1, len(test._new_snaps))

    def test_no_change_existing_but_same(self) -> None:
        test = Test("test_snap", tester, self.path)
        snap = Snapshot.new("test_snap", "snap", "this is content")
        snap.save_to(self.path / "test_snap" / f"snap.snap")
        test.snap("this is content", "snap")
        self.assertEqual(0, len(test._new_snaps))

    def tearDown(self) -> None:
        rmtree(self.path)


class TestRun(TestCase):

    @staticmethod
    def func_one(test: Test) -> None:
        test.snap("hello world!", "snap_1")
        test.snap("this is content", "snap_2")
        test.snap("my name is fred", "snap_3")

    @staticmethod
    def func_two(test: Test) -> None:
        test.snap("goodbye moon!", "snap_1")
        test.snap("this is content", "snap_2")
        test.snap("my name is greg", "snap_3")

    def call_function_and_strip_suffixes(self, test: Test, func: Callable) -> None:
        func(test)
        for file in self.path.rglob("*.new"):
            file.rename(file.with_suffix(""))

    def setUp(self) -> None:
        self.path = Path(mkdtemp())

    def test_reports_no_changes(self) -> None:
        test = Test("run_tester", self.func_one, self.path)
        self.call_function_and_strip_suffixes(test, self.func_one)
        test._run()
        self.assertEqual([], test._new_snaps)

    def test_reports_changed_files(self) -> None:
        test = Test("run_tester", self.func_two, self.path)
        self.call_function_and_strip_suffixes(test, self.func_one)
        test._run()
        self.assertEqual(['snap_1', 'snap_3'], test._new_snaps)

    def tearDown(self) -> None:
        rmtree(self.path)

