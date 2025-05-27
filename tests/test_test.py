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

        target_dir = self.path / "test_makes_snaps"
        files = [file.name for file in target_dir.glob("*.snap*")]

        self.assertEqual(['second_snap.snap.new', 'test_snap.snap.new'], files)

    def test_makes_new_snap_existing_but_different(self) -> None:
        test = Test("test_snap", tester, self.path)

        snap = Snapshot.new("test_snap", "snap", "this is content")
        snap.save_to(self.path / "test_snap" / f"snap.snap")

        test.snap("this is not content", "snap")
        files = list(self.path.rglob("*.snap*"))

        self.assertEqual(2, len(files))

    def test_no_change_existing_but_same(self) -> None:
        test = Test("test_snap", tester, self.path)

        snap = Snapshot.new("test_snap", "snap", "this is content")
        snap.save_to(self.path / "test_snap" / f"snap.snap")

        test.snap("this is content", "snap")
        files = list(self.path.rglob("*.snap*"))

        self.assertEqual(1, len(files))

    def tearDown(self) -> None:
        rmtree(self.path)

