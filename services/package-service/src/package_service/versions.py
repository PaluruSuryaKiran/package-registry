import re
from typing import NamedTuple

_Version_RE = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")

class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

def parse_version(version_str: str) -> Version:
    match = _Version_RE.fullmatch(version_str)
    if match is None:
        raise ValueError(f"Invalid version string: {version_str}")
    major, minor, patch = (int(part) for part in match.groups())
    return Version(major, minor, patch)