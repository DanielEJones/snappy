from unittest import TestCase
from io import StringIO

from snappy.snapshot import Snapshot, _load_snapshot


class TestSnapshotCreation(TestCase):

    def test_no_hash_no_content(self) -> None:
        self.assertRaises(ValueError, Snapshot, "test", "test")

    def test_hash_and_content(self) -> None:
        self.assertRaises(ValueError, Snapshot, "test", "test", "content", "hash")

    def test_hash_works_correct(self) -> None:
        left = Snapshot.new("test1", "test", "hello, world!\n")
        right = Snapshot.new("test2", "test", "hello, world!\n")
        self.assertTrue(left == right)

    def test_hash_works_incorrect(self) -> None:
        left = Snapshot.new("test1", "test", "hello, world!\n\n")
        right = Snapshot.new("test2", "test", "hello, world!\n")
        self.assertFalse(left == right)


class SnapshotLoader(TestCase):

    def test_loads_correct_snapshot_no_data(self) -> None:
        test = StringIO("---\nname: test\nsnap: test\nhash: bogus\n---\nhello, world!\n\n---")
        data = _load_snapshot(test, load_content=False)
        self.assertEqual({'name': 'test', 'snap': 'test', 'hash': 'bogus'}, data)

    def test_loads_correct_snapshot_data(self) -> None:
        test = StringIO("---\nname: test\nsnap: test\nhash: bogus\n---\nhello, world!\n\n---")
        data = _load_snapshot(test, load_content=True)
        self.assertEqual({'name': 'test', 'snap': 'test', 'content': 'hello, world!\n'}, data)

    def test_fails_incorrect_snapshot_no_data(self) -> None:
        test = StringIO("---\nname: test\nsnap: test\nhash: bogus\n")
        self.assertRaises(ValueError, lambda s: _load_snapshot(s, load_content=False), test)

    def test_fails_incorrect_snapshot_data(self) -> None:
        test = StringIO("---\nname: test\nsnap: test\nhash: bogus\n---\nhello, world!")
        self.assertRaises(ValueError, lambda s: _load_snapshot(s, load_content=True), test)


class SnapshotStringify(TestCase):

    def test_basic_snapshot(self) -> None:
        snap = Snapshot.new(test_name="test", snap_name="snap", content="hello, wolrd!")
        self.assertIn("---\ntest: test\nsnap: snap\n", str(snap))
        self.assertIn("hello, wolrd!\n---", str(snap))

    def test_can_load_saved_with_content(self) -> None:
        original = Snapshot.new(test_name="test", snap_name="snap", content="hello,\nworld!\n")
        saved = StringIO(str(original))
        loaded = _load_snapshot(saved, load_content=True)
        self.assertEqual(original._test, loaded["test"])
        self.assertEqual(original._snap, loaded["snap"])
        self.assertEqual(original._date, loaded["date"])
        self.assertEqual(original._content, loaded["content"])

        # Hash should be removed if loading content
        self.assertNotIn("hash", loaded)

    def test_can_load_saved_no_content(self) -> None:
        original = Snapshot.new(test_name="test", snap_name="snap", content="hello,\nworld!\n")
        saved = StringIO(str(original))
        loaded = _load_snapshot(saved, load_content=False)
        self.assertEqual(original._test, loaded["test"])
        self.assertEqual(original._snap, loaded["snap"])
        self.assertEqual(original._hash, loaded["hash"])
        self.assertEqual(original._date, loaded["date"])

        # Content should not appear if not loading
        self.assertNotIn("content", loaded)

