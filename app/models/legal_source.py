from dataclasses import dataclass
from typing import Optional


@dataclass
class LegalSource:
    title: str
    source_type: str
    jurisdiction: str
    article: Optional[str] = None
    text: str = ""
    source_url: Optional[str] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    language: str = "en"

    def is_current(self, date: str) -> bool:
        if self.effective_from and date < self.effective_from:
            return False

        if self.effective_to and date > self.effective_to:
            return False

        return True
