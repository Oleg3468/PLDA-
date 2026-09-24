from dataclasses import dataclass, field
from typing import List


@dataclass
class Case:
    case_id: str
    title: str
    jurisdiction: str
    facts: List[str] = field(default_factory=list)
    rights: List[str] = field(default_factory=list)
    arguments_for: List[str] = field(default_factory=list)
    arguments_against: List[str] = field(default_factory=list)
