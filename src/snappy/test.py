from __future__ import annotations

from typing import Callable
from pathlib import Path

from .snapshot import Snapshot
from .report import Report, Status


class Test:
    """
    Represents a test case, created by a Test Suite to wrap the actual test callable. This
    wrapper is passed to the callable and provides assertion methods, as well as facilitates
    test running and reporting.
    """

    def __init__(self, name: str, function: Callable[[Test], None], snap_directory: Path) -> None:
        """
        Creates a test case object and sets up the snap directory with the correct sub-directories
        for the test to save to.

        Args:
            name: the name of the test case, most likely derived from the function name.
            function: the callable that holds test logic.
            snap_directory: the path to the directory snapshots should be save to.
        """
        # These are constants for the lifespan of the test
        self._name = name
        self._function = function
        self._snap_directory = snap_directory / name

        # Prepare the snapshot directory
        self._snap_directory.mkdir(parents=True, exist_ok=True)

        # Used to track test state / results
        self.report = Report(self._name)


    def snap(self, capture_content: str, snap_name: str) -> None:
        """
        Creates a snapshot of the given content and compares it to the existing snapshot. If the
        existing snapshot does not exist or has a different hash, the new snapshot will be saved
        with a `.snap.new` extension for review.

        Args:
            capture_content: The string content to be saved in the snapshot.
            snap_name: The name under which the snapshot will be stored.
        """
        file_path = self._snap_directory / f"{snap_name}.snap"

        snap_report = self.report.get_child_by_path(snap_name)

        snap = Snapshot.new(
            test_name = self._name,
            snap_name = snap_name,
            content = capture_content
        )

        if file_path.exists():
            old = Snapshot.load_from(file_path)

            # If the old snap exists, and it matches the current one, we don't have to do anything
            # so simply return early
            if snap == old:
                snap_report.set_status(Status.OK)
                return

        # If we get here, either the file doesn't exist or it's different. Either way, save it with
        # the `.snap.new` extension for review later
        snap.save_to(file_path.with_suffix(".snap.new"))
        snap_report.set_status(Status.ERR)


    def _run(self, report: Report) -> None:
        # Any calls to snap made with in the function will be recorded
        # and used for test reporting by the suite
        self.report = report
        self._function(self)

