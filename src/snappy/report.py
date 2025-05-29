
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

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.children: List[Report] = []

        self._status = Status.RUNNING


    def add_child(self, child: Report) -> Report:
        self.children.append(child)
        return self


    def set_status(self, status: Status) -> Report:
        self._status = status
        return self


    def to_lines(self, indentation: int = 0) -> List[str]:
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

