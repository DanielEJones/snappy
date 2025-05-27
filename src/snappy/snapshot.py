from __future__ import annotations

from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from hashlib import sha256


def _hash_content(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _load_snapshot(path: Path, load_content: bool) -> dict[str, str]:
    ...


def _dump_snapshot(snapshot: Snapshot) -> str:
    ...


class Snapshot:
    """
    Represents a snapshot created during testing, either created in the test or
    loaded from a persistent file. Contains metadata useful for comparison,
    such as the content hash and time of creation.

    New snapshots should be created with `Snapshot.new`, and old ones should be
    created with `Snapshot.load`. Use `Snapshot.save` to persist a snapshot to a
    filepath.
    """


    def __init__(self,
        test_name: str, snap_name: str,
        content: Optional[str] = None,
        hash: Optional[str] = None,
        date: Optional[str] = None
    ) -> None:
        """
        Avoid using this initializer. Prefer instead to use `Snapshot.new` or
        `Snapshot.load` for creating new and loading old snapshots respectively.

        If you do use this, provide exactly one of `content` and `hash`. Providing
        both or providing neither is an error.

        Args:
            test_name: the name of the test creating the snapshot.
            snap_name: the name associated with the snapshot.
            content: the value to be stored as the body of the snapshot.
            hash: sha256 representation of content.
            date: the date of creation, defaulting to the current time.
        Raises:
            ValueError: if an incorrect combination of `hash` and `content` is provided.
        """
        self._test, self._snap = test_name, snap_name
        self._date = date or datetime.now(timezone.utc).isoformat()

        # We need exactly one of hash or content, anything else is a mistake
        if (hash is None) == (content is None):
            message = "both" if content else "none"
            raise ValueError(f"Expected exactly one of either `content` or `hash`: got {message}.")

        elif content:
            self._content = content
            self._hash = _hash_content(content)

        else:
            self._content = None
            self._hash = hash


    @classmethod
    def new(cls, test_name: str, snap_name: str, content: str) -> Snapshot:
        """
        Constructs a new snapshot.

        Args:
            test_name: the name of the test creating the snapshot.
            snap_name: the name associated with the snapshot.
            content: the value to be stored as the body of the snapshot.
        """
        return cls(test_name, snap_name, content)


    @classmethod
    def load_from(cls, path: Path, load_content: bool = False) -> Snapshot:
        """
        Loads an existing snapshot from a file path.

        Args:
            path: the location of the snapshot file.
            load_content: flag that determines if file content will be loaded, or just the hash.
        """
        return cls(**_load_snapshot(path, load_content))


    def save_to(self, path: Path) -> None:
        path.write_text(_dump_snapshot(self))

