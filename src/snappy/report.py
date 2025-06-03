from __future__ import annotations

from functools import reduce
from typing import List, Optional
from enum import StrEnum


class Status(StrEnum):
    RUNNING = "..."
    ERR = "Err!"
    OK = "Ok."


_STATUS_ORDER = { Status.OK: 0, Status.ERR: 1, Status.RUNNING: 2 }


SPACER = '  | '


class Report:
    """
    Represents a hierarchical test structure, where each leaf node represents an assertion.
    Printed in a pretty format that displays test status and summary, complete with nice ordering
    and folding completely passing subtests.
    """

    def __init__(self, name: str) -> None:
        """
        Creates a new report from a name.

        Args:
            name: the name you wish the report to be displayed as.
        """
        self.name: str = name
        self.children: List[Report] = []

        self._status = Status.RUNNING


    def add_child(self, child: Report) -> Report:
        """
        Adds a subtest to the current report. Returns a reference to self so
        that this method can be chained, enabling neat in-place report construction.

        Args:
            child: the new subtest to add.
        """
        self.children.append(child)
        return self


    def set_status(self, status: Status) -> Report:
        """
        Sets the current status to one of Running, Ok or Error. Returns a reference to
        self so that this method can be chained, enabling neat in-place report construction.

        Args:
            status: the value to set the status to.
        """
        self._status = status
        return self


    def to_lines(self, indentation: int = 0) -> List[str]:
        """
        Creates a representation of the report in a list-of-strings format. This will fold
        fully-passing subtests and sort children in the following priority:

            1. Is folded?
            2. Height
            3. Status (OK, ERR, RUNNING)
            4. Alphabetically
        """
        indent = SPACER * indentation

        if self.is_leaf():
            return [f"{indent}{self.name}: {self._status.value}"]

        if self.all_is(Status.OK):
            return [f"{indent}{self.name}: {self.child_count()} Ok."]

        self.children.sort(
            # 1. Folded suites should appear first
            # 2. Tallest children appear last
            # 3. Leaves sorted by OK -> ERR -> RUNNING
            # 4. If all else is equal, sort alphabetically
            key = lambda child: (
                not child.all_is(Status.OK),
                child.height(),
                _STATUS_ORDER[child._status],
                child.name
            )
        )

        lines = []
        for child in self.children:
            lines.extend(child.to_lines(indentation = indentation + 1))

        return [f"{indent}{self.name}/", *lines]


    def is_leaf(self) -> bool:
        return len(self.children) == 0


    def all_is(self, status: Status) -> bool:
        if self.is_leaf():
            return self._status == status
        return all(child.all_is(status) for child in self.children)


    def child_count(self) -> int:
        if self.is_leaf():
            return 1
        return sum(child.child_count() for child in self.children)


    def height(self) -> int:
        if self.is_leaf():
            return 0
        return 1 + max(child.height() for child in self.children)


    def get_child_by_name(self, name: str) -> Optional[Report]:
        return reduce(lambda result, new: new if new.name == name else result, self.children, None)


    def get_child_by_path(self, path: str) -> Report:
        """
        Returns a child node found at the given period-delimited path. If a child
        does not exist at that location, a new node (and all non-existant parents) will
        be created and a reference returned.

        A call to `report.get_child_by_path("child1.subchild.leaf")` is equivalent to calling
        `report.get_child_by_name("child1").get_child_by_name("subchild") ...`, except it will
        create a new node by the name if `get_child_by_name` ever returns None.

        Args:
            path: A period-deliminated string representing a path through the tree's children.
        """
        target = self
        for name in path.split('.'):
            node = target.get_child_by_name(name)
            if node is None:
                node = Report(name)
                target.add_child(node)
            target = node

        return target


    def __repr__(self) -> str:
        return '\n'.join(self.to_lines())

