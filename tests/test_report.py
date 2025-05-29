from unittest import TestCase

from snappy import report
from snappy.report import Report, Status


class TestHelpers(TestCase):

    def setUp(self) -> None:
        self.report = (
            Report("top")
                .add_child(Report("1st").set_status(Status.OK))
                .add_child(Report("2nd").set_status(Status.ERR))
                .add_child(Report("3rd").set_status(Status.RUNNING))
                .add_child(Report("nested")
                    .add_child(Report("inner_1").set_status(Status.OK))
                    .add_child(Report("inner_2").set_status(Status.OK))))

    def test_find_child_by_name_finds_correct(self) -> None:
        self.assertIsNotNone(self.report.get_child_by_name("2nd"))
        self.assertEqual("2nd", self.report.get_child_by_name("2nd").name) # type: ignore

    def test_find_child_by_name_fails_missing(self) -> None:
        self.assertIsNone(self.report.get_child_by_name("4th"))

    def test_get_child_by_path_finds_existing(self) -> None:
        self.assertEqual(Status.OK, self.report.get_child_by_path("nested.inner_2")._status)

    def test_get_child_by_path_creates_missing(self) -> None:
        count_before = self.report.child_count()
        self.assertEqual(Status.RUNNING, self.report.get_child_by_path("not.real.path")._status)
        self.assertEqual(count_before + 1, self.report.child_count())

    def test_all_is_correct(self) -> None:
        self.assertTrue(self.report.get_child_by_path("nested").all_is(Status.OK))

    def test_all_is_incorrect(self) -> None:
        self.assertFalse(self.report.get_child_by_path("nested").all_is(Status.ERR))


class TestFormatting(TestCase):

    def setUp(self) -> None:
        self.report = (
            Report("base")
                .add_child(Report("nested")
                    .add_child(Report("inner_1")
                        # Should be reordered in sorting
                        .add_child(Report("sub_2").set_status(Status.ERR))
                        .add_child(Report("sub_1").set_status(Status.RUNNING))
                        .add_child(Report("sub_3").set_status(Status.OK)))
                    .add_child(Report("inner_2")
                        # Should appear before `inner_1`
                        .add_child(Report("deepest")
                            .add_child(Report("innest").set_status(Status.ERR))))
                    .add_child(Report("inner_3")
                        # Should be collapsed
                        .add_child(Report("sub_1").set_status(Status.OK))
                        .add_child(Report("sub_2").set_status(Status.OK))))

                .add_child(Report("complex")
                    # Should be reordered
                    .add_child(Report("sub_2").set_status(Status.ERR))
                    .add_child(Report("sub_3").set_status(Status.RUNNING))
                    .add_child(Report("sub_1").set_status(Status.OK)))

                .add_child(Report("simple")
                    # Should be folded
                    .add_child(Report("sub_1").set_status(Status.OK))
                    .add_child(Report("sub_2").set_status(Status.OK))))

    def test_collapses_successes(self) -> None:
        self.assertIn(
            "simple: 2 Ok.",
            self.report.get_child_by_path("simple").to_lines())

    def test_doesnt_collapse_failures(self) -> None:
        self.assertIn(
            "complex/",
            self.report.get_child_by_path("complex").to_lines())

    def test_reorders_status(self) -> None:
        self.assertEqual(
            ["complex/",
             "  | sub_1: Ok.",
             "  | sub_2: Err!",
             "  | sub_3: ..."],
            self.report.get_child_by_path("complex").to_lines()
        )

    def test_deep_nesting(self) -> None:
        self.assertEqual(
            ["inner_2/",
             "  | deepest/",
             "  |   | innest: Err!"],
            self.report.get_child_by_path("nested.inner_2").to_lines()
        )

    def test_everything(self) -> None:
        self.assertEqual(
            ["nested/",
             "  | inner_3: 2 Ok.",
             "  | inner_1/",
             "  |   | sub_3: Ok.",
             "  |   | sub_2: Err!",
             "  |   | sub_1: ...",
             "  | inner_2/",
             "  |   | deepest/",
             "  |   |   | innest: Err!" ],
            self.report.get_child_by_path("nested").to_lines()
        )

